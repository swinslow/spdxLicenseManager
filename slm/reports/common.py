# reports/common.py
#
# Module for common reporting functions and exceptions for spdxLicenseManager.
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

class ReportFileError(Exception):
  """Exception raised for report file errors (e.g. invalid path or permission).

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class ReportNotReadyError(Exception):
  """Exception raised for trying to use or save report before it is ready.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class ReportAnalysisError(Exception):
  """Exception raised for error during analysis phase of report generation.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message
