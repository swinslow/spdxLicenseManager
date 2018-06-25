# tests/ft_reportsall.py
#
# Functional tests for spdxLicenseManager: producing all reports from
# all previously-imported scans, where not yet generated.
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
import json

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)
from helper_check import checkForFileExists

# paths to various SPDX test files
PATH_SIMPLE_SPDX = "tests/testfiles/simple.spdx"

class AllReportsFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager all-reporting FT suite."""

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

  ##### Tests below here

  def test_can_make_all_reports(self):
    # Edith wants to automatically have all types of reports created for
    # all currently-imported scans, for this project, that haven't already
    # been created with default paths
    result = runcmd(self, slm.cli, "frotz", "create-reports")

    # The output message tells her it succeeded
    self.assertEqual(0, result.exit_code)
    self.assertEqual("4 reports successfully created\n", result.output)

    # She checks to make sure, and indeed the reports are there
    p1 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.xlsx")
    checkForFileExists(self, self.slmhome, p1)
    p2 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.json")
    checkForFileExists(self, self.slmhome, p2)
    p3 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.xlsx")
    checkForFileExists(self, self.slmhome, p3)
    p4 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.json")
    checkForFileExists(self, self.slmhome, p4)

  def test_make_all_reports_does_not_recreate_existing_reports(self):
    # Edith creates a report with a standard path
    result = runcmd(self, slm.cli, "frotz",
      "create-report", "--scan_id", "1", "--report_format", "xlsx")
    # She checks to make sure, and indeed the report is there
    self.assertEqual(0, result.exit_code)
    p1 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.xlsx")
    checkForFileExists(self, self.slmhome, p1)

    # Now she wants to automatically have all types of reports created
    # for all currently-imported scans, for this project, but the
    # first report shouldn't be re-created
    result = runcmd(self, slm.cli, "frotz", "create-reports")

    # The output message tells her it succeeded and that only 3 reports
    # were created
    self.assertEqual(0, result.exit_code)
    self.assertEqual("3 reports successfully created\n", result.output)

    # She checks to make sure, and indeed the new reports are there
    checkForFileExists(self, self.slmhome, p1)
    p2 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.json")
    checkForFileExists(self, self.slmhome, p2)
    p3 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.xlsx")
    checkForFileExists(self, self.slmhome, p3)
    p4 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.json")
    checkForFileExists(self, self.slmhome, p4)

  def test_make_all_reports_can_recreate_existing_reports_if_forced(self):
    # Edith creates a report with a standard path
    result = runcmd(self, slm.cli, "frotz",
      "create-report", "--scan_id", "1", "--report_format", "xlsx")
    # She checks to make sure, and indeed the report is there
    self.assertEqual(0, result.exit_code)
    p1 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.xlsx")
    checkForFileExists(self, self.slmhome, p1)

    # Now she wants to automatically have all types of reports created
    # for all currently-imported scans, for this project. Existing
    # reports _should_ be re-created this time.
    result = runcmd(self, slm.cli, "frotz", "create-reports", "-f")

    # The output message tells her it succeeded and that all 4 reports
    # were created
    self.assertEqual(0, result.exit_code)
    self.assertEqual("4 reports successfully created\n", result.output)

    # She checks to make sure, and indeed the reports are all there
    checkForFileExists(self, self.slmhome, p1)
    p2 = os.path.join("projects", "frotz", "subprojects", "frotz-nuclear",
      "reports", "frotz-nuclear-2018-01-26.json")
    checkForFileExists(self, self.slmhome, p2)
    p3 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.xlsx")
    checkForFileExists(self, self.slmhome, p3)
    p4 = os.path.join("projects", "frotz", "subprojects", "frotz-dim",
      "reports", "frotz-dim-2018-02-06.json")
    checkForFileExists(self, self.slmhome, p4)
