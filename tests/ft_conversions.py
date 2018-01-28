# tests/ft_conversions.py
#
# Functional test for spdxLicenseManager: create, edit, list and delete
# conversions for license names.
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

class ConversionFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager license conversion create, edit, list and delete
  FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_add_and_retrieve_a_conversion(self):
    # Edith is creating a new conversion
    result = runcmd(self, slm.cli, "frotz", "add-conversion",
      "BSD-Simplified", "BSD-2-Clause")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created conversion: 'BSD-Simplified' => 'BSD-2-Clause'\n", result.output)

    # She retrieves the conversion to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "get-conversion", 'BSD-Simplified')
    self.assertEqual(0, result.exit_code)
    self.assertIn("BSD-2-Clause", result.output)

  def test_cannot_add_a_conversion_without_a_license(self):
    # Edith accidentally forgets to specify a license when trying to add
    # a new conversion
    result = runcmd(self, slm.cli, 'frotz', 'add-conversion', 'will fail')

    # It fails and explains why
    self.assertEqual(2, result.exit_code)
    self.assertEqual(f'Usage: {slm.cli.name} add-conversion [OPTIONS] OLD_TEXT LICENSE_NAME\n\nError: Missing argument "license_name".\n',result.output)

  def test_cannot_add_a_conversion_with_a_nonexistent_license(self):
    # Edith tries to add a new conversion, but accidentally specifies a
    # license that doesn't exist yet
    result = runcmd(self, slm.cli, 'frotz', 'add-conversion',
      'BSD-New', 'BSD-3-Clause')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"License 'BSD-3-Clause' does not exist yet.\nDid you mean to call add-license first?\n", result.output)

  def test_cannot_add_a_duplicate_conversion(self):
    # Edith tries to add a new conversion, but accidentally specifies text
    # that matches an existing conversion
    runcmd(self, slm.cli, 'frotz', 'add-conversion',
      'BSD-Simplified', 'BSD-2-Clause')
    result = runcmd(self, slm.cli, 'frotz', 'add-conversion',
      'BSD-Simplified', 'MIT')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Conversion 'BSD-Simplified' already exists.\n",result.output)

  def test_can_change_a_conversion_to_a_different_license(self):
    # Edith assigned BSD-Simplified to BSD-3-Clause, but then realized that
    # it should have been BSD-2-Clause instead
    runcmd(self, slm.cli, "frotz",
      "add-license", "BSD-3-Clause", "Attribution")
    runcmd(self, slm.cli, 'frotz',
      'add-conversion', 'BSD-Simplified', 'BSD-3-Clause')
    result = runcmd(self, slm.cli, 'frotz',
      'edit-conversion', 'BSD-Simplified', 'BSD-2-Clause')
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Updated license for conversion of BSD-Simplified to BSD-2-Clause\n", result.output)

    # When viewing the conversion, BSD-2-Clause is now listed
    result = runcmd(self, slm.cli, "frotz", "get-conversion", 'BSD-Simplified')
    self.assertEqual(0, result.exit_code)
    self.assertIn("BSD-2-Clause", result.output)

  def test_cannot_change_a_conversion_to_a_nonexistent_license(self):
    # Edith assigned BSD-Simplified to BSD-2-Clause, and then accidentally
    # tries to change it to a nonexistent license
    runcmd(self, slm.cli, 'frotz',
      'add-conversion', 'BSD-Simplified', 'BSD-2-Clause')
    result = runcmd(self, slm.cli, 'frotz',
      'edit-conversion', 'BSD-Simplified', 'BSD-2-Clause-FreeBSD')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"License 'BSD-2-Clause-FreeBSD' does not exist yet.\nDid you mean to call add-license first?\n", result.output)

  def test_cannot_change_a_nonexistent_conversion(self):
    # Edith accidentally tries to BSD-Simplified to BSD-2-Clause, but has
    # not created it yet
    result = runcmd(self, slm.cli, 'frotz',
      'edit-conversion', 'BSD-Simplified', 'BSD-2-Clause')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Conversion 'BSD-Simplified' does not exist in project frotz.\nDid you mean to call add-conversion instead?\n", result.output)

  def test_can_list_conversions(self):
    # Edith wants to see what conversions are already present
    result = runcmd(self, slm.cli, 'frotz', 'list-conversions')

    # The list is formatted in a helpful way
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"Expat => MIT\nGPL-2.0+ => GPL-2.0-or-later\nNOASSERTION => No license found\nNONE => No license found\n", result.output)
