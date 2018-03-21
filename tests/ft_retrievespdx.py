# tests/ft_retrievespdx.py
#
# Functional tests for spdxLicenseManager: retrieving SPDX files and placing
# them in the desired subproject directory.
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
import click
from click.testing import CliRunner
import shutil

from testfixtures import TempDirectory

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)
from helper_check import checkForFileExists, checkForDirectoryExists

# path to SPDX test files
PATH_SPDX_CORRECT_FILE = "tests/testfiles/SPDX2TV_spdxLicenseManager-2018-03-21.zip_1521659998.spdx"
PATH_SPDX_NO_NAME = "tests/testfiles/SPDX2TV_noname-2018-03-21.zip_1521659998.spdx"
PATH_SPDX_NO_DATE = "tests/testfiles/SPDX2TV_spdxLicenseManager-nodate.zip_1521659998.spdx"

class SPDXRetrieveFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX file retriever FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

    # set up temp directory for where SPDX files will be retrieved from
    self.spdxSearchDir = TempDirectory()

    # copy SPDX test files there
    shutil.copy(PATH_SPDX_CORRECT_FILE, self.spdxSearchDir.path)
    shutil.copy(PATH_SPDX_NO_NAME, self.spdxSearchDir.path)
    shutil.copy(PATH_SPDX_NO_DATE, self.spdxSearchDir.path)

  def tearDown(self):
    self.spdxSearchDir.cleanup()
    self.spdxSearchDir = None
    tearDownSandbox(self)

  def test_can_set_spdx_search_folder_config_var(self):
    # Edith wants to let SLM know that SPDX files for retrieval will be
    # stored in the spdx search directory
    result = runcmd(self, slm.cli, "frotz", "set-config",
      "spdx-search-dir", self.spdxSearchDir.path)
    self.assertEqual(0, result.exit_code)
