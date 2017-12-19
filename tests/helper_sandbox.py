# tests/helper_sandbox.py
#
# Helper for spdxLicenseManager: set up default sandbox for functional tests.
#
# Copyright (C) 2017 The Linux Foundation
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
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from testfixtures import TempDirectory

def setUpSandbox(self):
  # set up initial temp directory
  self.td = TempDirectory()

  # get paths to sandbox image and temp destination
  sandbox_src_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sandbox"
  )
  sandbox_dst_path = os.path.join(self.td.path, "sandbox")

  # copy subdirectories and contents
  shutil.copytree(sandbox_src_path, sandbox_dst_path)

  # set slmhome variable for test case
  self.slmhome = self.td.path

def tearDownSandbox(self):
  self.td.cleanup()
