# tests/ft_projects.py
#
# Functional test for spdxLicenseManager: list, create, and get info on
# projects and subprojects.
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
from helper_check import (checkForFileExists, checkForDirectoryExists,
  checkForTextInFile)

class ProjectTestSuite(unittest.TestCase):
  """spdxLicenseManager project list, create and info functional test suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_list_projects_and_subprojects(self):
    # Edith wants to see which top-level projects she is currently tracking
    # in spdxLicenseManager. She asks for a list of projects
    result = runcmd(self, slm.cli, None, "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("frotz\ngnusto\nrezrov\n", result.output)

    # She knows that frotz has multiple subprojects, so she asks for a list of
    # its subprojects
    result = runcmd(self, slm.cli, "frotz", "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual(result.output,
      "frotz/frotz-dim\nfrotz/frotz-nuclear\nfrotz/frotz-shiny\n")

  def test_can_get_desc_for_projects_when_listing_with_verbose_flag(self):
    # Edith wants to get descriptions too when she lists the projects
    # using the -v flag
    result = runcmd(self, slm.cli, None, "-v", "list")
    self.assertEqual(0, result.exit_code)
    self.assertIn("The FROTZ Project", result.output)

    # It also works with the --verbose flag
    result = runcmd(self, slm.cli, None, "--verbose", "list")
    self.assertEqual(0, result.exit_code)
    self.assertIn("The FROTZ Project", result.output)

  def test_can_get_subproject_details_when_listing_with_verbose_flag(self):
    # Edith wants to get descriptions and SPDX search strings too when she
    # lists the subprojects using the -v flag
    result = runcmd(self, slm.cli, "frotz", "-v", "list")
    self.assertEqual(0, result.exit_code)
    self.assertIn("FROTZ with nuclear settings", result.output)
    self.assertIn("will search SPDX files for: frotz-nuclear", result.output)

    # It also works with the --verbose flag
    result = runcmd(self, slm.cli, "frotz", "--verbose", "list")
    self.assertEqual(0, result.exit_code)
    self.assertIn("FROTZ with nuclear settings", result.output)
    self.assertIn("will search SPDX files for: frotz-nuclear", result.output)

  def test_can_create_new_project_and_subproject(self):
    # Edith is starting to manage licenses for a new project called yozozzo.
    # She asks SLM to create a new project
    result = runcmd(self, slm.cli, None, "create-project", "yozozzo",
      '--desc="The YOZOZZO Project"')
    self.assertEqual(0, result.exit_code)

    # She confirms that the SLM top-level configuration file has been updated
    # and now refers to yozozzo
    checkForTextInFile(self, self.slmhome, "slmconfig.json", "yozozzo")

    # She also confirms that the appropriate subdirectory and database have
    # been created
    checkForDirectoryExists(self, self.slmhome, "projects/yozozzo")
    checkForFileExists(self, self.slmhome, "projects/yozozzo/yozozzo.db")

    # And she confirms that a "reports/" subdirectory has been created for this
    # project
    checkForDirectoryExists(self, self.slmhome, "projects/yozozzo/reports")

    # And she confirms that a "list" command now includes yozozzo in the list
    result = runcmd(self, slm.cli, None, "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("frotz\ngnusto\nrezrov\nyozozzo\n", result.output)

    # Now, she wants to create its first subproject, yozozzo-duck
    result = runcmd(self, slm.cli, "yozozzo",
      "create-subproject", "yozozzo-duck",
      '--desc="Duck transformation spell"')
    self.assertEqual(0, result.exit_code)

    # She confirms that the appropriate subproject subdirectories have
    # been created
    checkForDirectoryExists(self, self.slmhome,
      "projects/yozozzo/yozozzo-duck")

    # And she confirms that the appropriate subdirectories have been created
    # for this subproject
    checkForDirectoryExists(self, self.slmhome, "projects/yozozzo/yozozzo-duck/spdx")
    checkForDirectoryExists(self, self.slmhome, "projects/yozozzo/yozozzo-duck/reports")

    # And she confirms that a "list" command now includes yozozzo-duck
    result = runcmd(self, slm.cli, "yozozzo", "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("yozozzo/yozozzo-duck\n", result.output)

  ##### NAMING AND CALLING TESTS

  def test_cannot_create_new_project_with_duplicate_name(self):
    # Edith accidentally asks SLM to create a new project with an existing name
    result = runcmd(self, slm.cli, None,
      "create-project", "frotz", '--desc="oops"')

    # It doesn't work and tells her why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(result.output, "Error: project frotz already exists\n")

  def test_cannot_create_new_project_and_also_pass_existing_project(self):
    # Edith asks SLM to create a new project, but accidentally also includes
    # an existing project name in the command
    result = runcmd(self, slm.cli, "frotz",
      "create-project", "yozozzo", '--desc="oops"')

    # It doesn't work and tells her why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(result.output, "Error: called create-project but passed project=frotz; did you mean to call create-subproject?\n")

  def test_project_with_no_desc_option_gets_NO_DESCRIPTION_text(self):
    # Edith asks SLM to create a new project, but accidentally omits the
    # "desc" option to the create-project command
    result = runcmd(self, slm.cli, None, "create-project", "nodesc")

    # It works fine, and sets the project description to NO DESCRIPTION
    self.assertEqual(0, result.exit_code)

    # ...which she confirms with a "list" call
    result = runcmd(self, slm.cli, None, "-v", "list")
    self.assertEqual(0, result.exit_code)
    self.assertIn("NO DESCRIPTION", result.output)

  def test_cannot_create_new_subproject_with_duplicate_name(self):
    # Edith accidentally asks SLM to create a new subproject with an existing
    # name under the same project
    result = runcmd(self, slm.cli, "frotz",
      "create-subproject", "frotz-dim", '--desc="oops"')

    # It doesn't work and tells her why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(result.output, "Error: subproject frotz-dim already exists for project frotz\n")

  def test_cannot_create_new_subproject_without_existing_project(self):
    # Edith asks SLM to create a new subproject, but accidentally also fails
    # to include an existing project name in the command
    result = runcmd(self, slm.cli, None,
      "create-subproject", "oops", '--desc="oops"')

    # It doesn't work and tells her why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(result.output, "Error: called create-subproject but didn't pass a project name; did you mean to call create-project?\n")
