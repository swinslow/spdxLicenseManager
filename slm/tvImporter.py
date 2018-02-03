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

from .projectdb import ProjectDBInsertError

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
      raise ProjectDBInsertError("Must call checkFileDataList before importing")

    # set up and import files
    file_tuples = []
    for fd in fdList:
      # create tuples with args in order from projectdb.addBulkFiles
      lic_id = self.licensesMapping.get(fd.license, None)
      if lic_id is None:
        raise ProjectDBInsertError(f"Error, license {fd.license} not found after checking all licenses; shouldn't happen")
      ft = (fd.path, lic_id, fd.sha1, fd.md5, fd.sha256)
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

  def _checkFileDataListForLicenses(self, fdList, db):
    # import all FDs into licenses set so we can see what's unknown
    lset = set()
    for fd in fdList:
      lset.add(fd.license)
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

    return self.licensesUnknown == []

  def _checkFileDataListForDuplicatePaths(self, fdList):
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
    self.errorMessage = ""
    self.importedCount = 0
