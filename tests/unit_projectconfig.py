# tests/unit_projectconfig.py
#
# Unit test for spdxLicenseManager: project-specific configuration.
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

from slm.projectconfig import ProjectConfig, BadProjectConfigError

class ProjectConfigTestSuite(unittest.TestCase):
  """spdxLicenseManager project configuration unit test suite."""

  def setUp(self):
    self.prjconfig_json = """{
      "subprojects": [
        { "name": "sub1", "desc": "subproject 1" },
        { "name": "sub3", "desc": "subproject the third" },
        { "name": "sub2", "desc": "subproject B" }
      ]
    }"""

  def tearDown(self):
    pass

  def DISABLE_test_can_parse_valid_project_config_file_for_subprojects(self):
    prjconfig = ProjectConfig()
    numSubprojects = prjconfig.loadConfig(self.prjconfig_json)
    self.assertEqual(numSubprojects, 3)
    self.assertEqual(len(prjconfig.subprojects), 3)
    self.assertEqual(prjconfig.getSubprojectDesc("sub2"), "subproject B")

  def DISABLE_test_raises_exception_for_subproject_with_no_name(self):
    badconfig_json = """{"subprojects": [ {"desc": "no name given"} ]}"""
    badconfig = ProjectConfig()
    with self.assertRaises(BadProjectConfigError):
      badconfig.loadConfig(badconfig_json)

  def DISABLE_test_raises_exception_for_duplicate_subproject_names(self):
    badconfig_json = """{
      "subprojects": [
        { "name": "subprj1", "desc": "The subprj Project" },
        { "name": "subprj1", "desc": "duplicate name -- should fail" }
      ]
    }"""
    badconfig = ProjectConfig()
    with self.assertRaises(BadProjectConfigError):
      badconfig.loadConfig(badconfig_json)

  def DISABLE_test_subprojects_are_sorted_when_listed(self):
    prjconfig = ProjectConfig()
    numSubprojects = prjconfig.loadConfig(self.prjconfig_json)
    self.assertEqual(prjconfig.subprojects[0].name, "sub1")
    self.assertEqual(prjconfig.subprojects[1].name, "sub2")
    self.assertEqual(prjconfig.subprojects[2].name, "sub3")

  def DISABLE_test_new_projectconfig_has_empty_subprojects(self):
    prjconfig = ProjectConfig()
    self.assertFalse(prjconfig.subprojects)

  def DISABLE_test_can_add_new_subproject(self):
    prjconfig = ProjectConfig()
    prjconfig.loadConfig(self.prjconfig_json)
    numSubprojects = prjconfig.addSubproject("sub4", "The 4th Subproject")
    self.assertEqual(numSubprojects, 4)
    self.assertEqual(len(prjconfig.subprojects), 4)
    self.assertEqual(prjconfig.getSubprojectDesc("sub4"), "The 4th Subproject")

  def DISABLE_test_prjconfig_json_updated_to_include_new_subproject(self):
    # load default and add new subproject
    prjconfig = ProjectConfig()
    prjconfig.loadConfig(self.prjconfig_json)
    prjconfig.addSubproject("sub4", "The 4th Subproject")

    # get JSON back and recreate in new config
    new_json = prjconfig.getJSON()
    newconfig = ProjectConfig()
    newconfig.loadConfig(new_json)

    # check that the old and new subprojects are present
    self.assertEqual(len(newconfig.subprojects), 4)
    self.assertEqual(newconfig.getSubprojectDesc("sub4"), "The 4th Subproject")
    self.assertEqual(newconfig.getSubprojectDesc("sub1"), "subproject 1")
    self.assertEqual(newconfig.getSubprojectDesc("sub2"), "subproject B")
    self.assertEqual(newconfig.getSubprojectDesc("sub3"), "subproject the third")

  def DISABLE_test_subprojects_are_sorted_after_new_subproject_is_added(self):
    prjconfig = ProjectConfig()
    prjconfig.loadConfig(self.prjconfig_json)
    prjconfig.addSubproject("sub2.5", "The 2.5th Subproject")
    self.assertEqual(prjconfig.subprojects[0].name, "sub1")
    self.assertEqual(prjconfig.subprojects[1].name, "sub2")
    self.assertEqual(prjconfig.subprojects[2].name, "sub2.5")
    self.assertEqual(prjconfig.subprojects[3].name, "sub3")

  def DISABLE_test_cannot_add_duplicate_subproject_name(self):
    prjconfig = ProjectConfig()
    prjconfig.loadConfig(self.prjconfig_json)
    with self.assertRaises(BadProjectConfigError):
      prjconfig.addSubproject("sub1", "duplicate name - should fail")
