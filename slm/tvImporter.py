# tvImporter.py
#
# Module to read and clean a list of relevant file data, and import it into
# a project database, for spdxLicenseManager importing tag-value files.
#
# Copyright (C) The Linux Foundation
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from .projectdb import ProjectDBInsertError, ProjectDBQueryError

class TVImporter:
  def __init__(self):
    super(TVImporter, self).__init__()
    self._reset()

  ##### Main tag-value importing functions
  ##### External usage shouldn't require calling anything except these

  def checkFileDataList(self, *, fdList=None, db=None):
    if fdList is None:
      raise ProjectDBInsertError("Cannot check FileData list without providing list to import")
    if db is None:
      raise ProjectDBInsertError("Cannot check FileData list without providing database")

    # apply conversions
    self._applyConversions(fdList=fdList, db=db)

    # apply removal of common path prefixes, if config value is set
    self._applyPathPrefixStrip(fdList=fdList, db=db)

    # check filenames and return early if any are duplicates
    retval = self._checkFileDataListForDuplicatePaths(fdList=fdList)
    if retval is False:
      return False

    # check licenses and return early if any are unknown
    retval = self._checkFileDataListForLicenses(fdList=fdList, db=db)
    if retval is False:
      return False

    # all good
    self.scanChecked = True
    return True

  def importFileDataList(self, *, fdList=None, db=None, scan_id=None):
    if fdList is None:
      raise ProjectDBInsertError("Cannot import FileData list without providing list to import")
    if db is None:
      raise ProjectDBInsertError("Cannot import FileData list without providing database")
    if scan_id is None:
      raise ProjectDBInsertError("Cannot import FileData list without providing scan ID")

    # fails if not checked first
    if self.scanChecked != True:
      raise ProjectDBInsertError("Must successfully pass checkFileDataList before importing")

    # set up and import files
    file_tuples = []
    for fd in fdList:
      # create tuples with args in order from projectdb.addBulkFiles
      lic_id = self.licensesMapping.get(fd.finalLicense, None)
      if lic_id is None:
        raise ProjectDBInsertError(f"Error, license {fd.finalLicense} not found after checking all licenses; shouldn't happen")
      ft = (fd.finalPath, lic_id, fd.sha1, fd.md5, fd.sha256)
      file_tuples.append(ft)
    db.addBulkFiles(scan_id=scan_id, file_tuples=file_tuples)
    self.importedCount = len(file_tuples)
    return True

  def getUnknowns(self):
    return self.licensesUnknown

  def getImportedCount(self):
    return self.importedCount

  def getDuplicatePaths(self):
    return self.pathDuplicates

  ##### Tag-value importing main helper functions

  def _applyConversions(self, fdList, db):
    # load all conversions once, so we don't have to keep querying the database
    convsList = db.getConversionsAll()

    # convert to a dict for easier lookups
    convsDict = {}
    for conv in convsList:
      convsDict[conv.old_text] = conv.new_license.name

    # for each license, check whether we have a conversion available
    for fd in fdList:
      fd.finalLicense = convsDict.get(fd.license, fd.license)

  def _applyPathPrefixStrip(self, fdList, db):
    paths = [fd.path for fd in fdList]

    # set prefix to "" unless the right config value is set
    try:
      isStrip = str(db.getConfigValue("import-strip-path-prefixes"))
    except ProjectDBQueryError:
      isStrip = "no"

    if isStrip.lower() == "yes":
      try:
        prefix = os.path.commonpath(paths)
      except ValueError:
        # means that we were mixing absolute and relative paths
        # which also means that there's no common prefix
        prefix = ""
    else:
      prefix = ""

    # fill in finalPath either way, but only strip prefix if config'd and found
    if prefix != None and prefix != '':
      startloc = len(prefix)
      for fd in fdList:
        fd.finalPath = fd.path[startloc:]
    else:
      for fd in fdList:
        fd.finalPath = fd.path
    return prefix

  def _checkFileDataListForLicenses(self, fdList, db):
    # import all FDs into licenses set so we can see what's unknown
    lset = set()
    for fd in fdList:
      lset.add(fd.finalLicense)
    self.licensesAll = sorted(list(lset))

    # FIXME add checks here for other license name cleanup
    # FIXME e.g. conversions, stripping "LicenseRef-", etc.

    # check which licenses are unknown
    ldict = db.getMultipleLicenses(self.licensesAll)
    for lic, _id in ldict.items():
      if _id is None:
        self.licensesUnknown.append(lic)
      else:
        self.licensesMapping[lic] = _id

    self.licensesUnknown.sort()

    return self.licensesUnknown == []

  def _checkFileDataListForDuplicatePaths(self, fdList):
    # this correctly checks path, not finalPath.
    # if there are duplicates, we want to report them back with the full
    # path, not the path with a potentially stripped prefix.
    paths = []
    for fd in fdList:
      paths.append(fd.path)
    paths.sort()

    # now scan through for duplicates, i.e. same as previous b/c sorted
    dupPathsSet = set()
    priorPath = None
    for path in paths:
      if path == priorPath:
        dupPathsSet.add(path)
      priorPath = path

    # convert dup set to a sorted list
    self.pathDuplicates = sorted(list(dupPathsSet))

    return self.pathDuplicates == []

  ##### Other helper functions

  def _reset(self):
    self.scanChecked = False
    self.licensesAll = []
    self.licensesUnknown = []
    self.pathDuplicates = []
    self.licensesMapping = {}
    self.importedCount = 0
