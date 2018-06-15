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
  runcmd, printResultDebug)

class ComponentFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager component create, edit and list FT suite."""

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

  def test_can_add_and_retrieve_a_component_type(self):
    # Edith is creating a new component type
    result = runcmd(self, slm.cli, "frotz", "add-component-type", "Ruby")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created component type: Ruby\n",
      result.output)

    # She checks the list of component types to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-component-types")
    self.assertEqual(0, result.exit_code)
    self.assertIn("Ruby", result.output)

  def test_cannot_add_an_existing_component_type(self):
    # Edith accidentally tries to create a new component type with an
    # existing name
    result = runcmd(self, slm.cli, "frotz", "add-component-type", "Golang")

    # It fails and lets her know why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Component type 'Golang' already exists for project frotz.\n",
      result.output)

  def test_can_add_and_retrieve_a_component(self):
    # Edith is creating a new component for an existing scan
    result = runcmd(self, slm.cli, "frotz", "add-component",
      "github.com/spf13/pflag",
      "--scan_id", 3, "--component_type", "Golang")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created component for scan 3: github.com/spf13/pflag (Golang)\n",
      result.output)

    # She checks the list of components to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-components", "--scan_id", 3)
    self.assertEqual(0, result.exit_code)
    self.assertIn("github.com/spf13/pflag", result.output)

  def test_can_add_licenses_to_component(self):
    # Edith adds a component
    result = runcmd(self, slm.cli, "frotz", "add-component",
      "github.com/xanzy/ssh-agent",
      "--scan_id", 3, "--component_type", "Golang")
    self.assertEqual(0, result.exit_code)

    # She tags it as being subject to a license
    result = runcmd(self, slm.cli, "frotz", "add-component-license",
      "github.com/xanzy/ssh-agent", "Apache-2.0", "--scan_id", 3)

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Added Apache-2.0 to github.com/xanzy/ssh-agent for scan 3\n",
      result.output)

    # She tags it as being subject to a second license as well
    result = runcmd(self, slm.cli, "frotz", "add-component-license",
      "github.com/xanzy/ssh-agent", "MIT", "--scan_id", 3)

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Added MIT to github.com/xanzy/ssh-agent for scan 3\n",
      result.output)

  def test_can_get_verbose_details(self):
    # Edith adds a component
    result = runcmd(self, slm.cli, "frotz", "add-component",
      "github.com/xanzy/ssh-agent",
      "--scan_id", 3, "--component_type", "Golang")
    self.assertEqual(0, result.exit_code)

    # She adds some licenses to it
    result = runcmd(self, slm.cli, "frotz", "add-component-license",
      "github.com/xanzy/ssh-agent", "Apache-2.0", "--scan_id", 3)
    self.assertEqual(0, result.exit_code)
    result = runcmd(self, slm.cli, "frotz", "add-component-license",
      "github.com/xanzy/ssh-agent", "MIT", "--scan_id", 3)
    self.assertEqual(0, result.exit_code)

    # She checks to make sure she can get verbose details
    result = runcmd(self, slm.cli, "frotz", "-v", "list-components", "--scan_id", 3)
    self.assertEqual(0, result.exit_code)
    self.assertEqual("github.com/xanzy/ssh-agent:\n  licenses: Apache-2.0, MIT\n  type: Golang\n", result.output)

  # def test_can_get_urls_where_appropriate(self):
  #   # Edith adds a component
  #   result = runcmd(self, slm.cli, "frotz", "--scan_id", 3,
  #     "add-component", "github.com/spf13/pflag", "--type", "Golang")
  #   self.assertEqual(0, result.exit_code)

  #   # She checks to see if the URL is parsed correctly
  #   result = runcmd(self, slm.cli, "frotz", "-v", "list-components", "--scan_id", 3)
  #   self.assertEqual(0, result.exit_code)
  #   self.assertEqual("github.com/spf13/pflag:\n  licenses: \n  type: Golang\n  url: github.com/spf13/pflag\n", result.output)
