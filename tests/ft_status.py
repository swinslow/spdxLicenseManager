# tests/ft_status.py
#
# Functional tests for spdxLicenseManager: getting status of projects'
# scans and reports for a given month.
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

class StatusFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager status FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_get_status_from_baseline(self):
    # Edith wants to know the current status of scanning for Feb. 2018,
    # as a tabulated report
    result = runcmd(self, slm.cli, None, "status", "2018-02")

    # It works and creates a status report
    self.assertEqual(0, result.exit_code)
    lines = result.output.splitlines()

    # There should be seven lines total: two for month header and blank line,
    # two for headers and header line, and one for each of three subprojects
    self.assertEqual(len(lines), 7)

    # The status report starts with the current month
    self.assertTrue(lines[0].startswith("Month: 2018-02"))

    # Project name should be repeated for each subproject. Subprojects should
    # be in alphabetical order
    sp_dim = lines[4].split()
    sp_nuclear = lines[5].split()
    sp_shiny = lines[6].split()
    self.assertEqual(sp_dim[0], "frotz")
    self.assertEqual(sp_dim[1], "frotz-dim")
    self.assertEqual(sp_nuclear[0], "frotz")
    self.assertEqual(sp_nuclear[1], "frotz-nuclear")
    self.assertEqual(sp_shiny[0], "frotz")
    self.assertEqual(sp_shiny[1], "frotz-shiny")

    # An asterisk is used to mark entries. There should be an imported scan
    # for frotz-dim, but nothing else for any subproject
    self.assertEqual(lines[4].count("*"), 1)
    self.assertEqual(lines[5].count("*"), 0)
    self.assertEqual(lines[6].count("*"), 0)

  def test_can_get_status_with_reports(self):
    # Edith creates reports, and then checks status again for Feb. 2018
    result = runcmd(self, slm.cli, "frotz", "create-reports")
    self.assertEqual(0, result.exit_code)
    result = runcmd(self, slm.cli, None, "status", "2018-02")
    self.assertEqual(0, result.exit_code)
    lines = result.output.splitlines()

    # This time, there should still be 7 lines total
    self.assertEqual(len(lines), 7)

    # The fifth line (index 4) should still be frotz-dim, but it should
    # now have 3 asterisks: 1 for scan, 1 for JSON and 1 for Xlsx
    self.assertIn("frotz-dim", lines[4])
    self.assertEqual(lines[4].count("*"), 3)

    # And the others should still be 0
    self.assertEqual(lines[5].count("*"), 0)
    self.assertEqual(lines[6].count("*"), 0)
