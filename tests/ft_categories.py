# tests/ft_categories.py
#
# Functional test for spdxLicenseManager: create, edit, and get info on
# categories of licenses.
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

class CategoryFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager license category create, edit and info FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_create_and_retrieve_a_category(self):
    # Edith is creating a new category of licenses with Advertising Clauses
    result = runcmd(self, slm.cli, "frotz", "add-category",
      '"Advertising Clauses"')

    # It worked correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created category 'Advertising Clauses'.\n",
      result.output)

    # She checks the list of categories to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertIn("Advertising Clauses", result.output)

  def test_cannot_add_an_existing_category(self):
    # Edith accidentally tries to re-create the Project Licenses category
    result = runcmd(self, slm.cli, "frotz", "add-category",
      '"Project Licenses"')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Category 'Project Licenses' already exists for project frotz.\n", result.output)
