# tests/unit_slmconfig.py
#
# Unit test for spdxLicenseManager: top-level SLM configuration.
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

from slm.slmconfig import SLMConfig, BadSLMConfigError, SLMProjectNotFoundError

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

  def test_raises_exception_for_duplicate_project_names(self):
    badconfig_json = """{
      "projects": [
        { "name": "frotz", "desc": "The FROTZ Project" },
        { "name": "frotz", "desc": "duplicate name -- should fail" }
      ]
    }"""
    badconfig = SLMConfig()
    with self.assertRaises(BadSLMConfigError):
      badconfig.loadConfig(badconfig_json)

  def test_projects_are_sorted_when_listed(self):
    mainconfig = SLMConfig()
    numProjects = mainconfig.loadConfig(self.mainconfig_json)
    self.assertEqual(mainconfig.projects[0].name, "frotz")
    self.assertEqual(mainconfig.projects[1].name, "gnusto")
    self.assertEqual(mainconfig.projects[2].name, "rezrov")

  def test_can_add_new_project(self):
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    numProjects = mainconfig.addProject("prj4", "The prj4 Project")
    self.assertEqual(numProjects, 4)
    self.assertEqual(len(mainconfig.projects), 4)
    self.assertEqual(mainconfig.getProjectDesc("prj4"), "The prj4 Project")

  def test_mainconfig_json_updated_to_include_new_project(self):
    # load default and add new project
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    mainconfig.addProject("prj4", "The prj4 Project")

    # get JSON back and recreate in new config
    new_json = mainconfig.getJSON()
    newconfig = SLMConfig()
    newconfig.loadConfig(new_json)

    # check that the old and new projects are present
    self.assertEqual(len(newconfig.projects), 4)
    self.assertEqual(newconfig.getProjectDesc("prj4"), "The prj4 Project")
    self.assertEqual(newconfig.getProjectDesc("frotz"), "The FROTZ Project")
    self.assertEqual(newconfig.getProjectDesc("gnusto"), "The GNUSTO Project")
    self.assertEqual(newconfig.getProjectDesc("rezrov"), "The REZROV Project")

  def test_projects_are_sorted_after_new_project_is_added(self):
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    mainconfig.addProject("prj4", "The prj4 Project")
    self.assertEqual(mainconfig.projects[0].name, "frotz")
    self.assertEqual(mainconfig.projects[1].name, "gnusto")
    self.assertEqual(mainconfig.projects[2].name, "prj4")
    self.assertEqual(mainconfig.projects[3].name, "rezrov")

  def test_cannot_add_duplicate_project_name(self):
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    with self.assertRaises(BadSLMConfigError):
      mainconfig.addProject("frotz", "duplicate name - should fail")

  def test_can_get_correct_project_database_path(self):
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    self.assertEqual(mainconfig.getDBRelativePath("rezrov"),
      "projects/rezrov/rezrov.db")

  def test_database_path_with_invalid_project_name_raises_config_error(self):
    mainconfig = SLMConfig()
    mainconfig.loadConfig(self.mainconfig_json)
    with self.assertRaises(SLMProjectNotFoundError):
      mainconfig.getDBRelativePath("oops")
