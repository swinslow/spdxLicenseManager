# tests/unit_dbsubproject.py
#
# Unit test for spdxLicenseManager: database functions for Subprojects.
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
from unittest import mock
from testfixtures import TempDirectory

from slm.projectdb import ProjectDB, ProjectDBQueryError
from slm.datatypes import Subproject

class DBSubprojectUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for subproject data in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleSubprojectData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleSubprojectData(self):
    subprojects = [
      Subproject(id=1, name="sub1", desc="subproject 1"),
      Subproject(id=2, name="subX", desc="subproject XYZ"),
      Subproject(id=3, name="subC", desc="subproject B"),
    ]
    self.db.session.bulk_save_objects(subprojects)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_subproject_names_and_descs(self):
    subprojects = self.db.getSubprojectsAll()
    self.assertIsInstance(subprojects, list)
    self.assertEqual(len(subprojects), 3)
    self.assertEqual(subprojects[0].id, 1)
    self.assertEqual(subprojects[0].name, "sub1")
    self.assertEqual(subprojects[0].desc, "subproject 1")

  def test_all_subprojects_are_sorted_by_name(self):
    subprojects = self.db.getSubprojectsAll()
    self.assertEqual(subprojects[0].name, "sub1")
    self.assertEqual(subprojects[1].name, "subC")
    self.assertEqual(subprojects[2].name, "subX")

  def test_can_retrieve_one_subproject_by_id(self):
    subproject = self.db.getSubproject(_id=2)
    self.assertEqual(subproject.name, "subX")
    self.assertEqual(subproject.desc, "subproject XYZ")

  def test_can_retrieve_one_subproject_by_name(self):
    subproject = self.db.getSubproject(name="subC")
    self.assertEqual(subproject.id, 3)
    self.assertEqual(subproject.desc, "subproject B")

  def test_cannot_retrieve_subproject_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getSubproject(_id=3, name="subC")

  def test_cannot_retrieve_subproject_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getSubproject()

  def test_cannot_retrieve_subproject_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getSubproject("subC")

  def test_returns_none_if_subproject_not_found_by_id(self):
    subproject = self.db.getSubproject(_id=17)
    self.assertIsNone(subproject)

  def test_returns_none_if_subproject_not_found_by_name(self):
    subproject = self.db.getSubproject(name="noSuchSubproject")
    self.assertIsNone(subproject)

  def test_can_add_and_retrieve_subproject(self):
    subproject_id = self.db.addSubproject("newsub", "subproject new")

    # confirm that we now have four subprojects
    subprojects = self.db.getSubprojectsAll()
    self.assertEqual(len(subprojects), 4)

    # and confirm that we can retrieve this one by name
    subproject = self.db.getSubproject(name="newsub")
    self.assertEqual(subproject.name, "newsub")
    self.assertEqual(subproject.desc, "subproject new")

    # and confirm that we can retrieve this one by id
    subproject = self.db.getSubproject(_id=4)
    self.assertEqual(subproject.name, "newsub")
    self.assertEqual(subproject.desc, "subproject new")

  def test_can_start_adding_but_rollback_subproject(self):
    subproject_id = self.db.addSubproject(name="newsub",
      desc="will rollback", commit=False)
    self.db.rollback()
    # confirm that we still only have three subprojects
    subprojects = self.db.getSubprojectsAll()
    self.assertEqual(len(subprojects), 3)
    # and confirm that this subproject ID doesn't exist in database
    subproject = self.db.getSubproject(_id=subproject_id)
    self.assertIsNone(subproject)

  def test_can_start_adding_and_then_commit_subprojects(self):
    s1_id = self.db.addSubproject(name="news1", desc="new sp 1", commit=False)
    s2_id = self.db.addSubproject(name="news2", desc="new sp 2", commit=False)
    self.db.commit()
    # confirm that we now have five subprojects
    subprojects = self.db.getSubprojectsAll()
    self.assertEqual(len(subprojects), 5)
