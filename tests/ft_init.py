# tests/ft_init.py
#
# Functional test for spdxLicenseManager: initialize a new SLM home directory.
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

import os
import unittest
import click
from click.testing import CliRunner
from testfixtures import TempDirectory

from helper_sandbox import setUpSandbox, tearDownSandbox

from slm import slm

class ProjectTestSuite(unittest.TestCase):
  """spdxLicenseManager project list, create and info functional test suite."""

  def setUp(self):
    self.runner = CliRunner()
    # set up initial temp directory
    self.maintd = TempDirectory()
    self.mainsandboxPath = os.path.join(self.maintd.path, "sandbox")

    # also create a real sandbox for the "existing SLM" test
    setUpSandbox(self)

  def tearDown(self):
    tearDownSandbox(self)
    self.maintd.cleanup()

  def test_can_initialize_a_new_SLM_home_directory(self):
    # Edith just downloaded spdxLicenseManager (yay!) She wants to get started
    # using it, so she initializes a new SLM home directory (which is a path
    # to a directory that doesn't exist yet)
    newhome = os.path.join(self.mainsandboxPath, "SLM")
    result = self.runner.invoke(slm.cli, ['init', newhome])
    self.assertEqual(0, result.exit_code)

    # She sees that the directory has been created, along with intermediate
    # directories as needed
    self.assertTrue(os.path.isdir(self.mainsandboxPath))
    self.assertTrue(os.path.isdir(newhome))

    # She sees that an initial "projects" subdirectory has been created
    projectsPath = os.path.join(newhome, "projects")
    self.assertTrue(os.path.isdir(newhome))

    # She sees that an initial slmconfig.json file has been created
    mainconfigPath = os.path.join(newhome, "slmconfig.json")
    self.assertTrue(os.path.isfile(mainconfigPath))

    # And she sees that it contains a reference to a "projects" variable
    with open(mainconfigPath, "r") as f:
      filedata = f.read()
      self.assertTrue('"projects":' in filedata)

  def test_cannot_initialize_an_existing_SLM_home_directory(self):
    # Edith accidentally tries to initialize an existing SLM home directory
    result = self.runner.invoke(slm.cli, ['init', self.slmhome])

    # SLM won't let her and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(result.output, f"Error: {self.slmhome} already appears to be an spdxLicenseManager directory.\nIf you REALLY want to re-initialize it, delete the entire directory and re-run this command.\n")
