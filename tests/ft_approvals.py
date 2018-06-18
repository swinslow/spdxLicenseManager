# tests/ft_approvals.py
#
# Functional test for spdxLicenseManager: create, edit, and list approvals.
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

class ApprovalFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager approval create, edit and list FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)
    result = runcmd(self, slm.cli, "frotz", "add-license",
      "BSD-3-Clause", "Attribution")
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", "tests/testfiles/godeps-example.spdx",
      "--scan_date", "2018-06-14", "--desc", "frotz-dim golang scan"
    )

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_add_and_retrieve_an_approval_type(self):
    # Edith wants to be able to mark components and files as approved by the TSC.
    # She creates a new approval type
    result = runcmd(self, slm.cli, "frotz", "add-approval-type", "TSC approval")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created approval type: TSC approval\n", result.output)

    # She checks the list of approval types to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-approval-types")
    self.assertEqual(0, result.exit_code)
    self.assertIn("TSC approval", result.output)

  # def test_can_approve_components(self):
  #   # Edith wants to approve some components. She creates a new approval type
  #   result = runcmd(self, slm.cli, "frotz", "add-approval-type",
  #     "TSC approval")
  #   self.assertEqual(0, result.exit_code)

  #   # She adds a component
  #   result = runcmd(self, slm.cli, "frotz", "add-component",
  #     "github.com/xanzy/ssh-agent",
  #     "--scan_id", 3, "--component_type", "Golang")
  #   self.assertEqual(0, result.exit_code)

  #   # She adds two licenses and a location
  #   result = runcmd(self, slm.cli, "frotz", "add-component-license",
  #     "github.com/xanzy/ssh-agent", "Apache-2.0", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   result = runcmd(self, slm.cli, "frotz", "add-component-license",
  #     "github.com/xanzy/ssh-agent", "MIT", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   result = runcmd(self, slm.cli, "frotz", "add-component-location",
  #     "github.com/xanzy/ssh-agent", "/vendor/github.com/xanzy/ssh-agent/", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)

  #   # Now, she marks that component as approved by the TSC
  #   result = runcmd(self, slm.cli, "frotz", "add-approval",
  #     "--component", "github.com/xanzy/ssh-agent", "TSC approval",
  #     "--date", "2018-05-01", "--scan_id", 3)

  #   # It works correctly and lets her know
  #   self.assertEqual(0, result.exit_code)
  #   self.assertEqual("github.com/xanzy/ssh-agent marked as approved by: TSC approval\n", result.output)

  #   # She checks the list of approvals for this scan to make sure, and there it is
  #   result = runcmd(self, slm.cli, "frotz", "list-approvals", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   self.assertEqual("Approved (1):\n  Apache-2.0 AND MIT: github.com/xanzy/ssh-agent\n", result.output)
