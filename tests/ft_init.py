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

from slm import slm

class ProjectTestSuite(unittest.TestCase):
  """spdxLicenseManager project list, create and info functional test suite."""

  def setUp(self):
    self.runner = CliRunner()
    # set up initial temp directory
    self.td = TempDirectory()
    self.sandboxPath = os.path.join(self.td.path, "sandbox")

  def tearDown(self):
    self.td.cleanup()

  def test_can_initialize_a_new_SLM_home_directory(self):
    # Edith just downloaded spdxLicenseManager (yay!) She wants to get started
    # using it, so she initializes a new SLM home directory (which is a path
    # to a directory that doesn't exist yet)
    slmhome = os.path.join(self.sandboxPath, "SLM")
    result = self.runner.invoke(slm.cli, ['init', slmhome])

    # She sees that the directory has been created, along with intermediate
    # directories as needed
    self.assertTrue(os.path.isdir(self.sandboxPath))
    self.assertTrue(os.path.isdir(slmhome))

    # She sees that an initial "projects" subdirectory has been created
    projectsPath = os.path.join(slmhome, "projects")
    self.assertTrue(os.path.isdir(slmhome))

    # She sees that an initial slmconfig.json file has been created
    mainconfigPath = os.path.join(slmhome, "slmconfig.json")
    self.assertTrue(os.path.isfile(mainconfigPath))

    # And she sees that it contains a reference to a "projects" variable
    with open(mainconfigPath, "r") as f:
      filedata = f.read()
      self.assertTrue('"projects":' in filedata)
