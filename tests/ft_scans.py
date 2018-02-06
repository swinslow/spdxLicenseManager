# tests/ft_scans.py
#
# Functional tests for spdxLicenseManager: handling scans.
# Note that functional tests for importing SPDX files are located in
#   tests/ft_import.py.
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

class SPDXScanFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager scan edit and list FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_list_scans(self):
    # Edith asks for a list of all current scans
    result = runcmd(self, slm.cli, "frotz", "list-scans")

    # they are sorted by ID, with correct column formatting
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"""\
Scans for project frotz:

ID  Subproject     Date        Description
==  ==========     ====        ===========
1   frotz-nuclear  2018-01-26  frotz-nuclear initial scan
2   frotz-dim      2018-02-06  frotz-dim initial scan
""", result.output)

  def test_can_list_scans_for_just_one_subproject(self):
    # Edith asks for a list of scans in just the frotz-dim subproject
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "list-scans")

    # only the frotz-dim scan is displayed
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"""\
Scans for project frotz, subproject frotz-dim:

ID  Subproject  Date        Description
==  ==========  ====        ===========
2   frotz-dim   2018-02-06  frotz-dim initial scan
""", result.output)

