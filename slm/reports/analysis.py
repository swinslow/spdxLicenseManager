# reports/analysis.py
#
# Module for analysis functions for spdxLicenseManager. Common to all reports
# regardless of output format.
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
from collections import OrderedDict

from .common import ReportAnalysisError
from ..projectdb import ProjectDBQueryError
from ..datatypes import Category, File, License

class Analyzer:

  MD5_EMPTY_FILE = "d41d8cd98f00b204e9800998ecf8427e"

  def __init__(self, db, config={}):
    super(Analyzer, self).__init__()
    self._reset()
    self.db = db
    # copy over config entries into new dict
    for key, value in config.items():
      self.kwConfig[key] = value

  ##### Main common report analysis functions
  ##### External usage shouldn't require calling anything except these

  def runAnalysis(self, scan_id):
    # check whether scan exists
    scan = self.db.getScan(_id=scan_id)
    if scan is None:
      raise ReportAnalysisError(f"Scan ID {scan_id} does not exist")

    # build and run analysis
    self._buildScanCategories()
    self._addFiles(scan_id=scan_id)
    self._runAnalysis()

    self.analysisDone = True
    return self.primaryScanCategories

  def getResultsAsList(self):
    if not self.analysisDone:
      raise ReportAnalysisError("Cannot call getResultsAsList before analysis has been run")

    listResults = []
    # create and add new categories
    for cat_id, cat in self.primaryScanCategories.items():
      newCat = Category(_id=cat_id, name=cat.name)
      newCat.licenses = []
      listResults.append(newCat)
      # create and add new licenses
      for lic_id, lic in cat.licensesSorted.items():
        newLic = License(_id=lic_id, name=lic.name)
        newLic.files = []
        newCat.licenses.append(newLic)
        for f_id, f in lic.filesSorted.items():
          newFile = File(_id=f_id, scan_id=f.scan_id, path=f.path,
            sha1=f.sha1, md5=f.md5, sha256=f.sha256
          )
          newFile.findings = f.findings
          newLic.files.append(newFile)
    return listResults

  ##### Reporting analysis main helper functions

  def _buildScanCategories(self):
    if self.primaryScanCategories != OrderedDict():
      raise ReportAnalysisError("Cannot call _buildScanCategories twice")

    cats = self.db.getCategoriesAll()
    for cat in cats:
      self.primaryScanCategories[cat._id] = cat
      cat.hasFiles = False
      # fill in sorted licenses
      cat.licensesSorted = OrderedDict()
      # licenses is a SQLAlcehmy InstrumentedList, with licenses already in
      # order by name (see backref in datatypes.py)
      # so we can just copy them into an OrderedDict, in order
      for license in cat.licenses:
        cat.licensesSorted[license._id] = license
        license.filesSorted = OrderedDict()
        license.hasFiles = False

  def _addFiles(self, scan_id):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _addFiles before _buildScanCategories")

    try:
      files = self.db.getFiles(scan_id=scan_id)
    except ProjectDBQueryError:
      raise ReportAnalysisError(f"Couldn't get files for scan {scan_id}")
    for file in files:
      # add empty findings dict
      file.findings = {}

      # and add to category => license mapping
      l_id = file.license._id
      c_id = file.license.category._id
      cat = self.primaryScanCategories[c_id]
      lic = cat.licensesSorted[l_id]
      lic.filesSorted[file._id] = file

      # and note that this category and this license have files
      cat.hasFiles = True
      lic.hasFiles = True

  def _runAnalysis(self):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _runAnalysis before _buildScanCategories")

    # run analyses based on config in DB, overridable by keywords
    if self._getFinalConfigValue('analyze-exclude-path-prefix') == "yes":
      self._analyzeExcludePathPrefix()
    if self._getFinalConfigValue('analyze-extensions') == "yes":
      self._analyzeExtensions()
    if self._getFinalConfigValue('analyze-thirdparty') == "yes":
      self._analyzeThirdparty()
    if self._getFinalConfigValue('analyze-emptyfile') == "yes":
      self._analyzeEmptyFile()

    # then run post-analysis modifications to results
    if self._getFinalConfigValue('analyze-exclude-empty-cats-and-lics') == "yes":
      self._analyzeExcludeEmptyCatsAndLics()

  def _analyzeExtensions(self):
    extList = self._parseExtConfig()
    for cat in self.primaryScanCategories.values():
      for lic in cat.licensesSorted.values():
        for file in lic.filesSorted.values():
          # get the extension from the tuple, and strip off the leading period
          ext = os.path.splitext(file.path)[1].lstrip(".")
          if ext in extList:
            file.findings["extension"] = "yes"

  def _analyzeThirdparty(self):
    dirList = self._parseDirConfig()
    for cat in self.primaryScanCategories.values():
      for lic in cat.licensesSorted.values():
        for file in lic.filesSorted.values():
          # check each directory in list to see if it's in this file's path
          for directory in dirList:
            if directory in file.path:
              file.findings["thirdparty"] = "yes"

  def _analyzeEmptyFile(self):
    for cat in self.primaryScanCategories.values():
      for lic in cat.licensesSorted.values():
        for file in lic.filesSorted.values():
          if file.md5 == self.MD5_EMPTY_FILE:
            file.findings["emptyfile"] = "yes"

  def _analyzeExcludePathPrefix(self):
    # first build a lsit of all file paths
    paths = []
    for cat in self.primaryScanCategories.values():
      for lic in cat.licensesSorted.values():
        for file in lic.filesSorted.values():
          paths.append(file.path)

    # see if there's a common prefix
    prefix = os.path.commonpath(paths)

    # if so, then go back through and remove it
    if paths != '' and paths != '/':
      for cat in self.primaryScanCategories.values():
        for lic in cat.licensesSorted.values():
          for file in lic.filesSorted.values():
            file.path = file.path[len(prefix):]

  def _analyzeExcludeEmptyCatsAndLics(self):
    # walk through and mark category keys to remove
    catsToDelete = []
    for cat_id, cat in self.primaryScanCategories.items():
      if cat.hasFiles == False:
        catsToDelete.append(cat_id)
    # now, delete those categories
    for cat_id in catsToDelete:
      del self.primaryScanCategories[cat_id]

    # next, walk back through the categories and check their licenses
    for cat in self.primaryScanCategories.values():
      licsToDelete = []
      for lic_id, lic in cat.licensesSorted.items():
        if lic.hasFiles == False:
          licsToDelete.append(lic_id)
      # and finally, within this category, delete those licenses
      for lic_id in licsToDelete:
        del cat.licensesSorted[lic_id]

  ##### Other helper functions

  def _reset(self):
    self.isReady = False
    self.primaryScan = None
    self.primaryScanCategories = OrderedDict()
    self.kwConfig = {}
    self.analysisDone = False

  def _getFinalConfigValue(self, key):
    kwValue = self.kwConfig.get(key, None)
    if kwValue is not None:
      return str(kwValue).lower()
    try:
      value = self.db.getConfigValue(key)
      return str(value).lower()
    except ProjectDBQueryError:
      return ""

  def _parseExtConfig(self):
    extString = self._getFinalConfigValue('analyze-extensions-list')
    if extString == '':
      return []

    extList = extString.split(';')
    extStripped = []
    for ext in extList:
      extStripped.append(ext.strip())
    return sorted(extStripped)

  def _parseDirConfig(self):
    dirString = self._getFinalConfigValue('analyze-thirdparty-dirs')
    if dirString == '':
      return []

    dirList = dirString.split(';')
    dirStripped = []
    for directory in dirList:
      dirStripped.append(directory.strip())
    return sorted(dirStripped)

  def _getCategory(self, category_id):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _getCategory before _buildScanCategories")
    return self.primaryScanCategories.get(category_id, None)

  def _getLicense(self, license_id):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _getLicense before _buildScanCategories")
    try:
      lic = self.db.getLicense(_id=license_id)
    except ProjectDBQueryError:
      return None
    if lic is None:
      return None

    c_id = lic.category_id
    cat = self.primaryScanCategories[c_id]
    if cat is None:
      return None
    return cat.licensesSorted.get(license_id, None)

  def _getFile(self, file_id):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _getFile before _buildScanCategories")
    try:
      f = self.db.getFile(_id=file_id)
    except ProjectDBQueryError:
      return None
    if f is None:
      return None

    l_id = f.license_id
    c_id = f.license.category_id
    cat = self.primaryScanCategories[c_id]
    if cat is None:
      return None
    lic = cat.licensesSorted[l_id]
    if lic is None:
      return None
    return lic.filesSorted.get(file_id, None)
