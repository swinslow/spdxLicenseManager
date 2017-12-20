# tests/ft_projects.py
#
# Functional test for spdxLicenseManager: list, create, and get info on
# projects and subprojects.
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

from helper_sandbox import setUpSandbox, tearDownSandbox, runcmd
from helper_check import (checkForFileExists, checkForDirectoryExists,
  checkForTextInFile)

class ProjectTestSuite(unittest.TestCase):
  """spdxLicenseManager project list, create and info functional test suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self)

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
    self.assertEqual("frotz/frotz-dim\nfrotz/frotz-nuclear\nfrotz/frotz-shiny\n", result.output)

  def test_can_create_new_project_and_subproject(self):
    # Edith is starting to manage licenses for a new project called yozozzo.
    # She asks SLM to create a new project
    result = runcmd(self, slm.cli, None, "create", "yozozzo", '--desc="The YOZOZZO Project"')
    self.assertEqual(0, result.exit_code)

    # She confirms that the SLM top-level configuration file has been updated
    # and now refers to yozozzo
    checkForTextInFile(self, self.slmhome, "slmconfig.json", "yozozzo")

    # She also confirms that the appropriate subdirectories and config files
    # have been created
    checkForDirectoryExists(self, self.slmhome, "projects/yozozzo")
    checkForFileExists(self, self.slmhome, "projects/yozozzo/yozozzo.config.json")

    # And she confirms that a "list" command now includes yozozzo in the list
    result = runcmd(self, slm.cli, None, "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("frotz\ngnusto\nrezrov\nyozozzo\n", result.output)

    # Now, she wants to create its first subproject, yozozzo-duck
    result = runcmd(self, slm.cli, yozozzo,
      "create", "yozozzo-duck", '--desc="Duck transformation spell"')
    self.assertEqual(0, result.exit_code)

    # She confirms that the project configuration file has been updated and
    # now refers to yozozzo-duck
    checkForTextInFile(self, self.slmhome,
      "projects/yozozzo/yozozzo.config.json", "yozozzo-duck")

    # She also confirms that the appropriate subproject subdirectories and
    # config files have been created
    checkForDirectoryExists(self, self.slmhome,
      "projects/yozozzo/yozozzo-duck")
    checkForFileExists(self, self.slmhome,
      "projects/yozozzo/yozozzo-duck/yozozzo-duck.config.json")

    # And she confirms that a "list" command now includes yozozzo-duck
    result = runcmd(self, slm.cli, "yozozzo", "list")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("yozozzo/yozozzo-duck\n", result.output)
