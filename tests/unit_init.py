# tests/unit_init.py
#
# Unit test for spdxLicenseManager: initializing a new SLM data directory.
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

import unittest
from unittest import mock

from slm.commands.cmdInit import createNewHomeDir, createNewProjectsDir

class InitTestSuite(unittest.TestCase):
  """spdxLicenseManager initialization unit test suite."""

  def setUp(self):
    pass

  def tearDown(self):
    pass

  @mock.patch('slm.commands.cmdInit.os.makedirs')
  def test_new_dirs_created_for_initialization(self, mock_os_makedirs):
    newhome = "/tmp/fake/slm"
    createNewHomeDir(newhome)
    mock_os_makedirs.assert_called_with(
      name="/tmp/fake/slm",
      mode=0o755,
      exist_ok=True
    )
    createNewProjectsDir(newhome)
    mock_os_makedirs.assert_called_with(
      name="/tmp/fake/slm/projects",
      mode=0o755
    )
