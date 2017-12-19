# tests/unit_slmconfig.py
#
# Unit test for spdxLicenseManager: top-level SLM configuration.
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

from slm.slmconfig import SLMConfig, BadSLMConfigError

class SLMConfigTestSuite(unittest.TestCase):
  """spdxLicenseManager SLM configuration unit test suite."""

  def setUp(self):
    self.mainconfig_json = """{
      "projects": [
        { "name": "frotz", "desc": "The FROTZ Project" },
        { "name": "rezrov", "desc": "The REZROV Project" },
        { "name": "gnusto", "desc": "The GNUSTO Project" }
      ]
    }"""

  def tearDown(self):
    pass

  def test_can_parse_valid_config_file_for_projects(self):
    mainconfig = SLMConfig()
    numProjects = mainconfig.loadConfig(self.mainconfig_json)
    self.assertEqual(numProjects, 3)
    self.assertEqual(len(mainconfig.projects), 3)
    self.assertEqual(mainconfig.getProjectDesc("frotz"), "The FROTZ Project")

  def test_raises_exception_for_project_with_no_name(self):
    badconfig_json = """{"projects": [ {"desc": "no name given"} ]}"""
    badconfig = SLMConfig()
    with self.assertRaises(BadSLMConfigError):
      badconfig.loadConfig(badconfig_json)

  def test_projects_are_sorted_when_listed(self):
    mainconfig = SLMConfig()
    numProjects = mainconfig.loadConfig(self.mainconfig_json)
    self.assertEqual(mainconfig.projects[0].name, "frotz")
    self.assertEqual(mainconfig.projects[1].name, "gnusto")
    self.assertEqual(mainconfig.projects[2].name, "rezrov")
