# tests/ft_components.py
#
# Functional test for spdxLicenseManager: create, edit, and list licenses.
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
  runcmd)

class ComponentFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager component create, edit and list FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", "tests/testfiles/golang-examples.spdx",
      "--scan_date", "2018-06-14", "--desc", "frotz-dim golang scan"
    )

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_add_and_retrieve_a_component(self):
    # Edith is creating a new component for an existing scan
    result = runcmd(self, slm.cli, "frotz", "--scan_id", 3,
      "add-component", "github.com/spf13/pflag", "--type", "Golang")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created component: github.com/spf13/pflag\n",
      result.output)

    # She checks the list of components to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-components", "--scan_id", 3)
    self.assertEqual(0, result.exit_code)
    self.assertIn("github.com/spf13/pflag", result.output)


  # def test_can_get_verbose_details(self):
  #   # Edith adds a component
  #   result = runcmd(self, slm.cli, "frotz", "--scan_id", 3,
  #     "add-component", "github.com/spf13/pflag", "--type", "Golang")
  #   self.assertEqual(0, result.exit_code)

  #   # She checks to make sure she can get verbose details
  #   result = runcmd(self, slm.cli, "frotz", "-v", "list-components", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   self.assertEqual("github.com/spf13/pflag:\n  licenses: \n  type: Golang\n  url: github.com/spf13/pflag\n", result.output)

  # def test_can_get_urls_where_appropriate(self):
  #   # Edith adds a component
  #   result = runcmd(self, slm.cli, "frotz", "--scan_id", 3,
  #     "add-component", "github.com/spf13/pflag", "--type", "Golang")
  #   self.assertEqual(0, result.exit_code)

  #   # She checks to see if the URL is parsed correctly
  #   result = runcmd(self, slm.cli, "frotz", "-v", "list-components", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   self.assertEqual("github.com/spf13/pflag:\n  licenses: \n  type: Golang\n  url: github.com/spf13/pflag\n", result.output)
