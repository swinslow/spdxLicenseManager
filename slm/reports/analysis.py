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

class Analyzer:

  def __init__(self, db):
    super(Analyzer, self).__init__()
    self.db = db
    self._reset()

  ##### Main common report analysis functions
  ##### External usage shouldn't require calling anything except these

  ##### Reporting analysis main helper functions

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
      l_id = file.license._id
      c_id = file.license.category._id
      cat = self.primaryScanCategories[c_id]
      lic = cat.licensesSorted[l_id]
      lic.filesSorted[file._id] = file

  ##### Other helper functions

  def _reset(self):
    self.isReady = False
    self.primaryScan = None
    self.primaryScanCategories = OrderedDict()
