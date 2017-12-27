# tests/unit_createproject.py
#
# Unit test for spdxLicenseManager: creating projects.
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
from unittest import mock

from slm.slmconfig import SLMConfig, BadSLMConfigError
from slm.commands.cmdCreate import (createNewProjectDirs,
  createNewSubprojectDirs)

class ProjectCreateTestSuite(unittest.TestCase):
  """spdxLicenseManager project creation unit test suite."""

  def setUp(self):
    self.mainconfig_json = """{
      "projects": [
        { "name": "prj1", "desc": "The prj1 Project" },
        { "name": "prj2", "desc": "The prj2 Project" }
      ]
    }"""

  def tearDown(self):
    pass

  @mock.patch('slm.commands.cmdCreate.os.makedirs')
  def test_new_dir_created_for_new_project(self, mock_os_makedirs):
    slmhome = "/tmp/fake/slm"
    createNewProjectDirs(slmhome, "newprj")
    mock_os_makedirs.assert_called_with(
      name="/tmp/fake/slm/projects/newprj",
      mode=0o755
    )

  @mock.patch('slm.commands.cmdCreate.os.makedirs')
  def test_new_dir_created_for_new_subproject(self, mock_os_makedirs):
    slmhome = "/tmp/fake/slm"
    createNewSubprojectDirs(slmhome, "newprj", "newsubprj")
    mock_os_makedirs.assert_called_with(
      name="/tmp/fake/slm/projects/newprj/newsubprj",
      mode=0o755
    )
