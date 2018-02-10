# tests/ft_report.py
#
# Functional tests for spdxLicenseManager: producing reports from previously-
# imported scans.
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

from testfixtures import TempDirectory
from openpyxl import load_workbook

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)
from helper_check import checkForFileExists

# paths to various SPDX test files
PATH_SIMPLE_SPDX = "tests/testfiles/simple.spdx"

class SPDXReportFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager tag-value reporting FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

    # set up temp directory for outputting reports
    self.reportDir = TempDirectory()

  def tearDown(self):
    self.reportDir.cleanup()
    self.reportDir = None
    tearDownSandbox(self)

  def test_can_create_simple_report_without_summary(self):
    # Edith imports a very short SPDX file as a new scan in the frotz
    # subproject frotz-dim
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")
    self.assertEqual(0, result.exit_code)

    # Now Edith wants to get an Excel report of the findings, sorted by
    # license category. She specifies the target output path and doesn't want
    # an initial summary sheet
    reportPath = self.reportDir.path + "/report.xlsx"
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "create-report", "--scan_id", "3", "--format", "xlsx",
      "--report-path", reportPath, "--no-summary")

    # She confirms that the file was created successfully
    self.assertEqual(0, result.exit_code)
    self.assertTrue(checkForFileExists(reportPath))

    # Looking inside the workbook, she sees that the expected license
    # sheets are present
    wb = load_workbook(filename=reportPath, read_only=True)
    self.assertEqual(['Attribution', 'No license found'], wb.get_sheet_names())

    # and that the appropriate headers are present
    # and that the file and license results are in the expected locations
    self.assertFail("Finish the test!")
