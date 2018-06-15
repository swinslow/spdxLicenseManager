# tests/unit_dbcomponent.py
#
# Unit test for spdxLicenseManager: database functions for ComponentTypes.
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
import datetime

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError)

from slm.datatypes import ComponentType

class DBComponentTypeUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for component types in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleComponentTypeData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleComponentTypeData(self):
    component_types = [
      ComponentType(_id=1, name="Python"),
      ComponentType(_id=2, name="JavaScript"),
      ComponentType(_id=3, name="Golang"),
    ]
    self.db.session.bulk_save_objects(component_types)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_component_types(self):
    componentTypes = self.db.getComponentTypesAll()
    self.assertIsInstance(componentTypes, list)
    self.assertEqual(len(componentTypes), 3)
    # ordered by ID
    self.assertEqual(componentTypes[0]._id, 1)
    self.assertEqual(componentTypes[0].name, "Python")

  def test_can_retrieve_one_component_type_by_id(self):
    componentType = self.db.getComponentType(_id=2)
    self.assertEqual(componentType.name, "JavaScript")

  def test_can_retrieve_one_component_type_by_name(self):
    componentType = self.db.getComponentType(name="JavaScript")
    self.assertEqual(componentType._id, 2)

  def test_cannot_retrieve_component_type_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentType(_id=3, name="Golang")

  def test_cannot_retrieve_component_type_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentType()

  def test_cannot_retrieve_component_type_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getComponentType("Golang")

  def test_returns_none_if_component_type_not_found_by_id(self):
    componentType = self.db.getComponentType(_id=17)
    self.assertIsNone(componentType)

  def test_returns_none_if_component_type_not_found_by_name(self):
    componentType = self.db.getComponentType(name="noSuchType")
    self.assertIsNone(componentType)

  def test_can_add_and_retrieve_component_types(self):
    componentType_id = self.db.addComponentType(name="C++")

    # confirm that we now have four component types
    componentTypes = self.db.getComponentTypesAll()
    self.assertEqual(len(componentTypes), 4)

    # and confirm that we can retrieve this one by id
    componentType = self.db.getComponentType(_id=4)
    self.assertEqual(componentType.name, "C++")

    # and confirm that we can retrieve this one by name
    componentType = self.db.getComponentType(name="C++")
    self.assertEqual(componentType._id, 4)

  def test_can_start_adding_but_rollback_component_type(self):
    componentType_id = self.db.addComponentType(name="will rollback",
      commit=False)
    self.db.rollback()
    # confirm that we still only have three component types
    componentTypes = self.db.getComponentTypesAll()
    self.assertEqual(len(componentTypes), 3)
    # and confirm that this component type ID doesn't exist in database
    componentType = self.db.getComponentType(_id=componentType_id)
    self.assertIsNone(componentType)

  def test_can_start_adding_and_then_commit_component_types(self):
    c1_id = self.db.addComponentType(name="newc1", commit=False)
    c2_id = self.db.addComponentType(name="newc2", commit=False)
    self.db.commit()
    # confirm that we now have five component types
    componentTypes = self.db.getComponentTypesAll()
    self.assertEqual(len(componentTypes), 5)

  def test_can_edit_component_type(self):
    self.db.changeComponentTypeName(name="JavaScript", newName="JS")
    componentType = self.db.getComponentType(name="JS")
    self.assertEqual(componentType._id, 2)

  def test_cannot_edit_component_type_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponentTypeName(name="invalid", newName="this will fail")

  def test_cannot_change_component_type_to_existing_name(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponentTypeName(name="JavaScript", newName="Golang")
