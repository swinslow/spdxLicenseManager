# tests/ft_reportjson.py
#
# Functional tests for spdxLicenseManager: producing JSON reports from 
# previously-imported scans.
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

class JSONReportFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager tag-value JSON reporting FT suite."""

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

  def test_can_create_simple_json_file_without_summary(self):
    # Edith imports a very short SPDX file as a new scan in the frotz
    # subproject frotz-dim
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")
    self.assertEqual(0, result.exit_code)

    # Now Edith wants to get a JSON version of the findings.
    # She configures it to omit empty categories and licenses
    result = runcmd(self, slm.cli, "frotz", "set-config", 
      "analyze-exclude-empty-cats-and-lics", "yes")
    self.assertEqual(0, result.exit_code)

    # And she requests the report and specifies the target output path
    reportPath = self.reportDir.path + "/report.json"
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "create-report", "--scan_id", "3", "--report_format", "json",
      "--report_path", reportPath)

    # The output message tells her it succeeded
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"Report successfully created at {reportPath}.\n", result.output)

    # She confirms that the file was created successfully
    self.assertTrue(os.path.isfile(reportPath))

    # Re-importing the JSON file, she sees that the expected values are present
    # in the expected format
    with open(reportPath, 'r') as f:
      rj = json.load(f)
      self.assertIsInstance(rj, list)
      self.assertEqual(len(rj), 2)
      cat1 = rj[0]
      self.assertEqual(cat1.get("name"), "Attribution")
      self.assertIsInstance(cat1.get("_id"), int)
      self.assertEqual(cat1.get("numFiles"), 1)
      cat1Lics = cat1.get("licenses")
      self.assertIsInstance(cat1Lics, list)
      self.assertEqual(len(cat1Lics), 1)
      lic1 = cat1Lics[0]
      self.assertEqual(lic1.get("name"), "MIT")
      self.assertIsInstance(lic1.get("_id"), int)
      self.assertEqual(lic1.get("numFiles"), 1)
      lic1Files = lic1.get("files")
      self.assertIsInstance(lic1Files, list)
      self.assertEqual(len(lic1Files), 1)
      file1 = lic1Files[0]
      self.assertEqual(file1.get("path"), "simple/file2.txt")
      self.assertIsInstance(file1.get("_id"), int)
      cat2 = rj[1]
      lic2 = cat2.get("licenses")[0]
      self.assertEqual(len(lic2.get("files")), 3)

  def test_can_omit_report_path_and_get_default_location_and_name(self):
    # Edith chooses not to include a --report-path flag
    result = runcmd(self, slm.cli, "frotz",
      "create-report", "--scan_id", "1", "--report_format", "json")

    # The output message tells her it succeeded, and that the report is in
    # the expected path and has the expected filename
    self.assertEqual(0, result.exit_code)
    expectedPath = os.path.join("projects", "frotz",
      "subprojects", "frotz-nuclear", "reports", "frotz-nuclear-2018-01.json")
    fullPath = os.path.join(self.slmhome, expectedPath)
    self.assertEqual(f"Report successfully created at {fullPath}.\n", result.output)

    # She checks to make sure, and indeed the report is there
    checkForFileExists(self, self.slmhome, expectedPath)
