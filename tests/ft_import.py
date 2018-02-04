# tests/ft_import.py
#
# Functional tests for spdxLicenseManager: import SPDX tag-value files.
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

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)

PATH_SIMPLE_ALL_KNOWN_SPDX = "tests/testfiles/simpleAllKnown.spdx"

class SPDXImportFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager tag-value importer FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_import_spdx_tag_value_file_and_get_results(self):
    # Edith has a very short SPDX file. She imports it as a new scan in
    # the frotz subproject frotz-dim
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_ALL_KNOWN_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It tells her that the scan was successfully added, and how to find it
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"Successfully imported 4 files from {PATH_SIMPLE_ALL_KNOWN_SPDX}\nScan ID is 1\n", result.output)

    # She now tries to print the scan results
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "list-scan-results", "--scan_id", "1")

    # They are displayed in a simple text format, alphabetically by file path
    self.assertEqual(0, result.exit_code)
    self.assertEqual(
f"""simple/dir1/subfile.txt => BSD-2-Clause
simple/file1.txt => BSD-2-Clause
simple/file2.txt => MIT
simple/file3.txt => BSD-2-Clause
""", result.output)

  def test_cannot_import_spdx_file_without_specifying_a_subproject(self):
    # Edith forgets to list a subproject when she tries to import an SPDX file
    result = runcmd(self, slm.cli, "frotz",
      "import-scan", PATH_SIMPLE_ALL_KNOWN_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f'Usage: slm --subproject SUBPROJECT import-scan SPDX_PATH [OPTIONS]\n\nError: Missing argument "subproject". Include "--subproject SUBPROJECT" before import-scan command, or set SLM_SUBPROJECT environment variable.\n',result.output)

  def test_cannot_import_spdx_file_that_does_not_exist(self):
    # Edith accidentally tries to import an SPDX file with an invalid path
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", "DOES_NOT_EXIST", "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f'File not found: DOES_NOT_EXIST\n',result.output)
