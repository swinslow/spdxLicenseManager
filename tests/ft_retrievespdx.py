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
import os
import shutil

from testfixtures import TempDirectory

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)
from helper_check import checkForFileExists, checkForDirectoryExists

# path to SPDX test files
SPDX_CORRECT_FILE = "SPDX2TV_frotz-dim-2018-03-21.zip_1521659998.spdx"
SPDX_NO_NAME = "SPDX2TV_noname-2018-03-21.zip_1521659998.spdx"
SPDX_NO_DATE = "SPDX2TV_frotz-dim-nodate.zip_1521659998.spdx"

class SPDXRetrieveFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX file retriever FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

    # set up temp directory for where SPDX files will be retrieved from
    self.spdxSearchDir = TempDirectory()

    # copy SPDX test files there
    shutil.copy(os.path.join("tests", "testfiles", SPDX_CORRECT_FILE),
      self.spdxSearchDir.path)
    shutil.copy(os.path.join("tests", "testfiles", SPDX_NO_NAME),
      self.spdxSearchDir.path)
    shutil.copy(os.path.join("tests", "testfiles", SPDX_NO_DATE),
      self.spdxSearchDir.path)

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

  def test_cannot_retrieve_spdx_files_if_no_search_folder_config_set(self):
    # Edith wants to have SLM automatically retrieve and rename SPDX files,
    # but mistakenly forgot to set the spdx search directory config variable
    result = runcmd(self, slm.cli, "frotz", "retrieve-spdx",
      "--month", "2018-03")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Configuration variable for SPDX search directory not found.\nPlease call 'slm set-config spdx-search-dir DIR_NAME' first.\n", result.output)

  def test_can_retrieve_spdx_files_and_move_to_subproject_folder(self):
    # Edith has set things correctly and asks SLM to retrieve, rename and move
    # the SPDX files for March 2018
    result = runcmd(self, slm.cli, "frotz", "set-config",
      "spdx-search-dir", self.spdxSearchDir.path)
    self.assertEqual(0, result.exit_code)

    result = runcmd(self, slm.cli, "frotz", "retrieve-spdx",
      "--month", "2018-03")

    # It works and lets her know
    self.assertEqual(0, result.exit_code)
    newName = "frotz-dim-2018-03-21.spdx"
    self.assertEqual(f"Moved {SPDX_CORRECT_FILE} to frotz-dim (new name: {newName})\n", result.output)

    # She sees that the file is now present in the subproject's SPDX folder
    filePath = os.path.join(self.slmhome, "projects", "frotz", 
      "subprojects", "frotz-dim", "spdx", newName)
    self.assertTrue(os.path.isfile(filePath))

    # And she sees that the file's old name is not present in the subproject's
    # SPDX folder
    filePath = os.path.join(self.slmhome, "projects", "frotz",
      "subprojects", "frotz-dim", "spdx", SPDX_CORRECT_FILE)
    self.assertFalse(os.path.isfile(filePath))

    # And she sees that the other two SPDX files with non-matching names are
    # not present in the subproject's SPDX folder
    filePath = os.path.join(self.slmhome, "projects", "frotz",
      "subprojects", "frotz-dim", "spdx", SPDX_NO_NAME)
    self.assertFalse(os.path.isfile(filePath))
    filePath = os.path.join(self.slmhome, "projects", "frotz",
      "subprojects", "frotz-dim", "spdx", SPDX_NO_DATE)
    self.assertFalse(os.path.isfile(filePath))

    # And she sees that it has been removed from the source search folder
    filePath = os.path.join(self.spdxSearchDir.path, SPDX_CORRECT_FILE)
    self.assertFalse(os.path.isfile(filePath))

    # And she sees that the other two SPDX files with non-matching names are
    # still present in the source search folder
    filePath = os.path.join(self.spdxSearchDir.path, SPDX_NO_NAME)
    self.assertTrue(os.path.isfile(filePath))
    filePath = os.path.join(self.spdxSearchDir.path, SPDX_NO_DATE)
    self.assertTrue(os.path.isfile(filePath))
