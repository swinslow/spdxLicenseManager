# tests/ft_categories.py
#
# Functional test for spdxLicenseManager: create, edit, and get info on
# categories of licenses.
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

class CategoryFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager license category create, edit and info FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_list_categories(self):
    # Edith asks for a list of all current categories
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Project Licenses\nCopyleft\nAttribution\nOther\nNo license found\n",
      result.output)

  def test_can_create_and_retrieve_a_category(self):
    # Edith is creating a new category of licenses with Advertising Clauses
    result = runcmd(self, slm.cli, "frotz", "add-category",
      "Advertising Clauses")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Created category: Advertising Clauses\n",
      result.output)

    # She checks the list of categories to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertIn("Advertising Clauses", result.output)

  def test_cannot_create_a_category_without_a_project(self):
    # Edith accidentally forgets to specify a project when trying to add
    # a new category
    result = runcmd(self, slm.cli, None, "add-category", 'whatever')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("No project specified.\nPlease specify a project with --project=PROJECT or the SLM_PROJECT environment variable.\n",result.output)

  def test_cannot_add_an_existing_category(self):
    # Edith accidentally tries to re-create the Project Licenses category
    result = runcmd(self, slm.cli, "frotz", "add-category",
      'Project Licenses')

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Category 'Project Licenses' already exists for project frotz.\n", result.output)

  def test_cannot_add_a_category_with_an_existing_order(self):
    # Edith accidentally tries to create a new category with the same order
    # value as the Attribution category
    result = runcmd(self, slm.cli, "frotz", "add-category",
      'Advertising Clause', "--order", 3)

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot create category 'Advertising Clause' with order 3 because category 'Attribution' already has order 3.\n", result.output)

  def test_cannot_add_a_category_with_order_less_than_one(self):
    # Edith accidentally tries to create a new category with order < 1
    result = runcmd(self, slm.cli, "frotz", "add-category",
      'Advertising Clause', "--order", 0)

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot create category 'Advertising Clause' with order 0; order value must be a positive integer.\n", result.output)

  def test_can_change_a_category_name(self):
    # Edith decides that the Attribution category should have been called
    # Permissive instead
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Attribution", "--new-name", "Permissive")
    self.assertEqual(0, result.exit_code)

    # When listing the categories, Permissive is now listed
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Project Licenses\nCopyleft\nPermissive\nOther\nNo license found\n",
      result.output)

  def test_cannot_edit_a_category_that_does_not_exist(self):
    # Edith tries to edit the Advertising Clauses category but forgets that it
    # doesn't exist yet
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Advertising Clause", "--new-name", "Obnoxious Notices")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Category 'Advertising Clause' does not exist in project frotz.\nDid you mean to call add-category instead?\n", result.output)

  def test_cannot_change_a_category_name_to_an_existing_name(self):
    # Edith accidentally tries to rename the Attribution category to Copyleft
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Attribution", "--new-name", "Copyleft")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot rename 'Attribution' category to 'Copyleft'; another category already has that name.\n", result.output)

  def test_cannot_edit_a_category_without_requesting_an_edit(self):
    # Edith accidentally edits a category but doesn't ask to change anything
    result = runcmd(self, slm.cli, "frotz", "edit-category", "Attribution")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("For edit-category, need to specify at least one of --new-name or --sort-before\n", result.output)

  def test_can_move_a_category_from_higher_to_lower(self):
    # Edith decides that she wants the attribution category to show up before
    # the copyleft category. She edits the categories to reorder them
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Attribution", "--sort-before", "Copyleft")
    self.assertEqual(0, result.exit_code)

    # When listing the categories, Attribution now shows up first
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Project Licenses\nAttribution\nCopyleft\nOther\nNo license found\n",
      result.output)

  def test_can_move_a_category_from_lower_to_higher(self):
    # Edith decides that she wants the project licenses category to show up
    # just before the attribution category. She edits the categories to
    # reorder them
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Project Licenses", "--sort-before", "Attribution")
    self.assertEqual(0, result.exit_code)

    # Category listing should be updated correctly now
    result = runcmd(self, slm.cli, "frotz", "list-categories")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Copyleft\nProject Licenses\nAttribution\nOther\nNo license found\n",
      result.output)

  def test_cannot_move_a_category_before_a_nonexistent_category(self):
    # Edith accidentally tries to move the Attribution category before the
    # Advertising Clause category, even though the latter doesn't exist yet
    result = runcmd(self, slm.cli, "frotz",
      "edit-category", "Attribution", "--sort-before", "Advertising Clause")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot sort 'Attribution' category before non-existent 'Advertising Clause' category\n", result.output)
