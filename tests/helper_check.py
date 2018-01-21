# tests/helper_check.py
#
# Helper for spdxLicenseManager: helpers with checks for functional tests.
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

def checkForFileExists(testCase, slmhome, path):
  filePath = os.path.join(slmhome, path)
  testCase.assertTrue(os.path.isfile(filePath))

def checkForDirectoryExists(testCase, slmhome, path):
  dirPath = os.path.join(slmhome, path)
  testCase.assertTrue(os.path.isdir(dirPath))

def checkForTextInFile(testCase, slmhome, path, text):
  filePath = os.path.join(slmhome, path)

  with open(filePath, "r") as f:
    filedata = f.read()
    testCase.assertTrue(text in filedata)
