# tests/ft_licenses.py
#
# Functional test for spdxLicenseManager: create, edit, and list licenses.
#
# Copyright (C) 2017 The Linux Foundation
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
#
# SPDX-License-Identifier: Apache-2.0

import unittest
import click
from click.testing import CliRunner

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd)

class LicenseFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager license create, edit and list FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_list_licenses(self):
    # Edith asks for a list of all current licenses
    result = runcmd(self, slm.cli, "frotz", "list-licenses")

    # they are sorted alphabetically
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Apache-2.0\nBSD-2-Clause\nCC-BY-4.0\nGPL-2.0-only\nGPL-2.0-or-later\nMIT\n",
      result.output)

  def test_can_add_and_retrieve_a_license(self):
    # Edith is creating a new license
    result = runcmd(self, slm.cli, "frotz", "add-license",
      "BSD-3-Clause", "Attribution")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created license: BSD-3-Clause\n",
      result.output)

    # She checks the list of categories to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-licenses")
    self.assertEqual(0, result.exit_code)
    self.assertIn("BSD-3-Clause", result.output)

  def test_cannot_add_a_license_without_a_project(self):
    # Edith accidentally forgets to specify a project when trying to add
    # a new license
    result = runcmd(self, slm.cli, None, 'add-license',
      'will fail', 'Attribution')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("No project specified.\nPlease specify a project with --project=PROJECT or the SLM_PROJECT environment variable.\n",result.output)

  def test_cannot_add_a_license_without_a_category(self):
    # Edith accidentally forgets to specify a category when trying to add
    # a new license
    result = runcmd(self, slm.cli, 'frotz', 'add-license', 'will fail')

    # It fails and explains why
    self.assertEqual(2, result.exit_code)
    self.assertEqual(f'Usage: {slm.cli.name} add-license [OPTIONS] NAME CATEGORY\n\nError: Missing argument "category".\n',result.output)

  def test_cannot_add_a_license_without_an_existing_category(self):
    # Edith accidentally tries to create a license with a non-existent category
    result = runcmd(self, slm.cli, 'frotz', 'add-license',
      'CC0', 'Public Domain')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Category 'Public Domain' does not exist.\n", result.output)

  def test_cannot_add_an_existing_license(self):
    # Edith accidentally tries to re-create the BSD-2-Clause license
    result = runcmd(self, slm.cli, "frotz", "add-license",
      'BSD-2-Clause', 'Copyleft')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("License 'BSD-2-Clause' already exists.\n", result.output)