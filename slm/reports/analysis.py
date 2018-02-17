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

class Analyzer:

  def __init__(self, db, config={}):
    super(Analyzer, self).__init__()
    self._reset()
    self.db = db
    # copy over config entries into new dict
    for key, value in config.items():
      self.kwConfig[key] = value

  ##### Main common report analysis functions
  ##### External usage shouldn't require calling anything except these

  ##### Reporting analysis main helper functions

  def _getFinalConfigValue(self, key):
    kwValue = self.kwConfig.get(key, None)
    if kwValue is not None:
      return str(kwValue).lower()
    try:
      value = self.db.getConfigValue(key)
      return str(value).lower()
    except ProjectDBQueryError:
      return ""

  def _buildScanCategories(self):
    if self.primaryScanCategories != OrderedDict():
      raise ReportAnalysisError("Cannot call _buildScanCategories twice")

    cats = self.db.getCategoriesAll()
    for cat in cats:
      self.primaryScanCategories[cat._id] = cat
      # fill in sorted licenses
      cat.licensesSorted = OrderedDict()
      # licenses is a SQLAlcehmy InstrumentedList, with licenses already in
      # order by name (see backref in datatypes.py)
      # so we can just copy them into an OrderedDict, in order
      for license in cat.licenses:
        cat.licensesSorted[license._id] = license
        license.filesSorted = OrderedDict()

  def _addFiles(self, scan_id):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _addFiles before _buildScanCategories")

    files = self.db.getFiles(scan_id=scan_id)
    for file in files:
      # add empty findings dict
      file.findings = {}

      # and add to category => license mapping
      l_id = file.license._id
      c_id = file.license.category._id
      cat = self.primaryScanCategories[c_id]
      lic = cat.licensesSorted[l_id]
      lic.filesSorted[file._id] = file

  def _runAnalysis(self):
    if self.primaryScanCategories == OrderedDict():
      raise ReportAnalysisError("Cannot call _runAnalysis before _buildScanCategories")

    # run analyses based on config in DB, overridable by keywords
    if self._getFinalConfigValue('analyze-extensions') == "yes":
      self._analyzeExtensions()
    if self._getFinalConfigValue('analyze-thirdparty') == "yes":
      self._analyzeThirdparty()
    if self._getFinalConfigValue('analyze-emptyfile') == "yes":
      self._analyzeEmptyFile()

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
    pass

  def _analyzeEmptyFile(self):
    pass

  ##### Other helper functions

  def _reset(self):
    self.isReady = False
    self.primaryScan = None
    self.primaryScanCategories = OrderedDict()
    self.kwConfig = {}

  def _parseExtConfig(self):
    extString = self._getFinalConfigValue('analyze-extensions-list')
    if extString == '':
      return []

    extList = extString.split(';')
    extStripped = []
    for ext in extList:
      extStripped.append(ext.strip())
    return sorted(extStripped)

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
