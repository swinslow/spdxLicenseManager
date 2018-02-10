# reports/xlsx.py
#
# Module for xlsx report generation functions for spdxLicenseManager.
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
import openpyxl

from .common import ReportFileError, ReportNotReadyError

class ExcelReporter:

  def __init__(self):
    super(ExcelReporter, self).__init__()
    self._reset()

  ##### Main xlsx reporting functions
  ##### External usage shouldn't require calling anything except these

  def save(self, path, replace=False):
    if not self.isReady:
      raise ReportNotReadyError("Cannot call save() before report is ready")

  ##### Other helper functions

  def _reset(self):
    self.isReady = False
    self.wb = None
