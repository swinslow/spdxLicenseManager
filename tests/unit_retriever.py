# tests/unit_retriever.py
#
# Unit test for spdxLicenseManager: retrieving SPDX files.
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

import os
import unittest
from unittest import mock

from slm.retriever import Retriever, RetrieverConfigError
from slm.datatypes import Subproject

class RetrieverTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX retrieval unit test suite."""

  def setUp(self):
    # create retriever object
    self.retriever = Retriever()

  def tearDown(self):
    pass

  ##### Test cases below

  def test_new_retriever_is_in_expected_reset_state(self):
    self.assertEqual(self.retriever.subprojects, {})
    self.assertEqual(self.retriever.datestr, "")
    self.assertEqual(self.retriever.search_dir, "")
    self.assertEqual(self.retriever.project_dir, "")
    self.assertEqual(self.retriever.results, {})

  ##### Getter and setter tests

  def test_can_set_datestr(self):
    self.retriever.setDatestr("2018-06")
    self.assertEqual("2018-06", self.retriever.datestr)

  def test_can_clear_datestr(self):
    self.retriever.setDatestr("")
    self.assertEqual("", self.retriever.datestr)

  def test_cannot_set_datestr_to_invalid_values(self):
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("blah")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018 06")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018-06-09")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018-30")
    self.assertEqual("", self.retriever.datestr)

  def test_can_add_subproject_ids_and_spdx_search_strings(self):
    self.retriever.addSubproject(spdx_search="subA", _id=1)
    self.retriever.addSubproject(spdx_search="sC", _id=3)
    self.retriever.addSubproject(spdx_search="subX", _id=2)
    _id, files = self.retriever.subprojects.get("sC")
    self.assertEqual(3, _id)
    self.assertEqual([], files)

  def test_cannot_add_subproject_ids_or_spdx_search_with_invalid_types(self):
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search="", _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search=None, _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search=1, _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search="hi", _id=0)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search="hi", _id=-1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search="hi", _id=None)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(spdx_search="hi", _id="blah")
    self.assertEqual({}, self.retriever.subprojects)

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  def test_can_set_directories_to_existing_directories(self, mock_isdir):
    downloadsDir = "/tmp/fake/Downloads/directory"
    self.retriever.setSearchDir(downloadsDir)
    self.assertEqual(downloadsDir, self.retriever.search_dir)
    projectDir = "/tmp/fake/SLM/fakeproject"
    self.retriever.setProjectDir(projectDir)
    self.assertEqual(projectDir, self.retriever.project_dir)

  @mock.patch("slm.retriever.os.path.isdir", return_value=False)
  def test_cannot_set_directories_to_nonexistent_directories(self, mock_isdir):
    downloadsDir = "/tmp/fake/invalid/directory"
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setSearchDir(downloadsDir)
    self.assertEqual("", self.retriever.search_dir)
    projectDir = "/tmp/fake/invalid/non-project/directory"
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setSearchDir(projectDir)
    self.assertEqual("", self.retriever.project_dir)
