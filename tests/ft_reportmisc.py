# tests/ft_reportmisc.py
#
# Functional tests for spdxLicenseManager: miscellaneous report-related tests.
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
import os

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)
from helper_check import checkForFileExists

# paths to various SPDX test files
PATH_SIMPLE_SPDX = "tests/testfiles/simple.spdx"

class MiscReportFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager tag-value miscellaneous reporting FT suite."""

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

  def test_cannot_request_an_invalid_report_format(self):
    # Edith asks for a report in a format that doesn't exist
    reportPath = self.reportDir.path + "/report.xlsx"
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-nuclear",
      "create-report", "--scan_id", "1", "--report_format", "blah",
      "--report_path", reportPath)

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Unknown report format: blah\n", result.output)
