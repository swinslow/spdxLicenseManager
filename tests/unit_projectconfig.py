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

  def test_can_parse_valid_project_config_file_for_subprojects(self):
    prjconfig = ProjectConfig()
    numSubprojects = prjconfig.loadConfig(self.prjconfig_json)
    self.assertEqual(numSubprojects, 3)
    self.assertEqual(len(prjconfig.subprojects), 3)
    self.assertEqual(prjconfig.getSubprojectDesc("sub2"), "subproject B")

  def test_raises_exception_for_subproject_with_no_name(self):
    badconfig_json = """{"subprojects": [ {"desc": "no name given"} ]}"""
    badconfig = ProjectConfig()
    with self.assertRaises(BadProjectConfigError):
      badconfig.loadConfig(badconfig_json)

  def test_raises_exception_for_duplicate_subproject_names(self):
    badconfig_json = """{
      "subprojects": [
        { "name": "subprj1", "desc": "The subprj Project" },
        { "name": "subprj1", "desc": "duplicate name -- should fail" }
      ]
    }"""
    badconfig = ProjectConfig()
    with self.assertRaises(BadProjectConfigError):
      badconfig.loadConfig(badconfig_json)

  def test_subprojects_are_sorted_when_listed(self):
    prjconfig = ProjectConfig()
    numSubprojects = prjconfig.loadConfig(self.prjconfig_json)
    self.assertEqual(prjconfig.subprojects[0].name, "sub1")
    self.assertEqual(prjconfig.subprojects[1].name, "sub2")
    self.assertEqual(prjconfig.subprojects[2].name, "sub3")

  def test_new_projectconfig_has_empty_subdir(self):
    prjconfig = ProjectConfig()
    self.assertFalse(prjconfig.subprojects)
