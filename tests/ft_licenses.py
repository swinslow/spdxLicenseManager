# tests/ft_licenses.py
#
# Functional test for spdxLicenseManager: create, edit, and list licenses.
#
# Copyright (C) The Linux Foundation
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
  runcmd, printResultDebug)

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

  def test_can_list_licenses_by_category(self):
    # Edith asks for a list of all current licenses, sorted by category
    result = runcmd(self, slm.cli, "frotz", "list-licenses", "--by-category")

    # they are sorted in category order and subsorted alphabetically
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Project Licenses:\n  Apache-2.0\n  CC-BY-4.0\nCopyleft:\n  GPL-2.0-only\n  GPL-2.0-or-later\nAttribution:\n  BSD-2-Clause\n  MIT\n",
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

  def test_can_change_a_license_name(self):
    # Edith decides that the BSD-2-Clause license should have been called
    # BSD-Simplified instead
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "BSD-2-Clause", "--new-name", "BSD-Simplified")
    self.assertEqual(0, result.exit_code)

    # When listing the license, BSD-Simplified is now listed
    result = runcmd(self, slm.cli, "frotz", "list-licenses")
    self.assertEqual(0, result.exit_code)
    self.assertIn("BSD-Simplified", result.output)
    self.assertNotIn("BSD-2-Clause", result.output)

  def test_can_change_a_license_category(self):
    # Edith decides that the BSD-2-Clause license should have been in the
    # Copyleft category instead (for some reason)
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "BSD-2-Clause", "--new-cat", "Copyleft")
    self.assertEqual(0, result.exit_code)

    # When listing the license, BSD-2-Clause is now listed in Copyleft
    result = runcmd(self, slm.cli, "frotz", "list-licenses", "--by-category")
    self.assertEqual(0, result.exit_code)
    self.assertIn("Copyleft:\n  BSD-2-Clause", result.output)
    self.assertNotIn("Attribution:\n  BSD-2-Clause", result.output)

  def test_cannot_change_a_license_to_a_category_that_does_not_exist(self):
    # Edith decides that the BSD-2-Clause license should have been in the
    # Advertising Clauses category, but it does not exist
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "BSD-2-Clause", "--new-cat", "Advertising Clauses")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Category 'Advertising Clauses' does not exist.\n",
      result.output)

  def test_cannot_edit_a_license_that_does_not_exist(self):
    # Edith tries to edit the CDDL-1.0 license but forgets that it
    # doesn't exist yet
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "CDDL-1.0", "--new-name", "CDDL-1.0+")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("License 'CDDL-1.0' does not exist in project frotz.\nDid you mean to call add-license instead?\n", result.output)

  def test_cannot_change_a_license_name_to_an_existing_name(self):
    # Edith accidentally tries to rename the BSD-2-Clause license to MIT
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "BSD-2-Clause", "--new-name", "MIT")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot rename 'BSD-2-Clause' license to 'MIT'; another license already has that name.\n", result.output)

  def test_cannot_change_a_license_name_to_itself(self):
    # Edith accidentally tries to rename the MIT license to MIT
    result = runcmd(self, slm.cli, "frotz",
      "edit-license", "MIT", "--new-name", "MIT")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot rename 'MIT' to itself.\n", result.output)

  def test_cannot_edit_a_license_without_requesting_an_edit(self):
    # Edith accidentally edits a license but doesn't ask to change anything
    result = runcmd(self, slm.cli, "frotz", "edit-license", "BSD-2-Clause")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("For edit-license, need to specify at least one of --new-name or --new-cat\n", result.output)
