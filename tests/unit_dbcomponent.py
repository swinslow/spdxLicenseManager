# tests/unit_dbcomponent.py
#
# Unit test for spdxLicenseManager: database functions for Components.
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

from slm.datatypes import (Category, Component, ComponentType, File,
  License, Scan, Subproject)

class DBComponentUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for components in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()
    self.insertSampleLicenseData()
    self.insertSampleSubprojectData()
    self.insertSampleScanData()
    self.insertSampleFileData()
    self.insertSampleComponentTypeData()
    self.insertSampleComponentData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleCategoryData(self):
    categories = [
      Category(_id=1, name="a category", order=3),
      Category(_id=2, name="cat", order=2),
      Category(_id=3, name="blah category", order=1),
    ]
    self.db.session.bulk_save_objects(categories)
    self.db.session.commit()

  def insertSampleLicenseData(self):
    licenses = [
      License(_id=1, name="DoAnything", category_id=1),
      License(_id=2, name="HarshEULA", category_id=2),
      License(_id=3, name="293PageEULA", category_id=3),
      License(_id=4, name="DoAnythingNoncommercial", category_id=1),
    ]
    self.db.session.bulk_save_objects(licenses)
    self.db.session.commit()

  def insertSampleSubprojectData(self):
    subprojects = [
      Subproject(_id=1, name="sub1", desc="subproject 1"),
      Subproject(_id=2, name="subX", desc="subproject XYZ"),
      Subproject(_id=3, name="subC", desc="subproject B"),
    ]
    self.db.session.bulk_save_objects(subprojects)
    self.db.session.commit()

  def insertSampleScanData(self):
    scans = [
      Scan(_id=1, subproject_id=2, scan_dt=datetime.date(2017, 1, 10),
        desc="XYZ initial scan"),
      Scan(_id=2, subproject_id=1, scan_dt=datetime.date(2017, 1, 3),
        desc="1 initial scan"),
      Scan(_id=3, subproject_id=2, scan_dt=datetime.date(2017, 2, 10),
        desc="XYZ 2017-02 monthly scan"),
      Scan(_id=4, subproject_id=2, scan_dt=datetime.date(2017, 2, 17),
        desc="XYZ 2017-02 rescan"),
    ]
    self.db.session.bulk_save_objects(scans)
    self.db.session.commit()

  def insertSampleFileData(self):
    files = [
      File(_id=1, scan_id=1, path="/fileC.c", license_id=1,
        sha1="aabbcc", md5="ddeeff", sha256="aaccee"),
      File(_id=2, scan_id=1, path="/fileA.c", license_id=1,
        sha1="112233", md5="445566", sha256="778899"),
      File(_id=3, scan_id=1, path="/fileB.c", license_id=2,
        sha1=None, md5=None, sha256=None),
      File(_id=4, scan_id=1, path="/dir/fileA.c", license_id=4,
        sha1="123456", md5="789012", sha256="345678"),
    ]
    self.db.session.bulk_save_objects(files)
    self.db.session.commit()

  def insertSampleComponentTypeData(self):
    component_types = [
      ComponentType(_id=1, name="Python"),
      ComponentType(_id=2, name="JavaScript"),
      ComponentType(_id=3, name="Golang"),
    ]
    self.db.session.bulk_save_objects(component_types)
    self.db.session.commit()

  def insertSampleComponentData(self):
    components = [
      Component(_id=1, scan_id=1, component_type_id=3,
        name="github.com/swinslow/peridot"),
      Component(_id=2, scan_id=1, component_type_id=2,
        name="jQuery"),
      Component(_id=3, scan_id=2, component_type_id=1,
        name="spdxLicenseManager"),
      Component(_id=4, scan_id=1, component_type_id=1,
        name="spdxLicenseManager"),
    ]
    self.db.session.bulk_save_objects(components)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_components(self):
    components = self.db.getComponentsAll()
    self.assertIsInstance(components, list)
    self.assertEqual(len(components), 4)
    # ordered by ID
    self.assertEqual(components[0]._id, 1)
    self.assertEqual(components[0].name, "github.com/swinslow/peridot")
    # and includes components across all scans
    self.assertEqual(components[2]._id, 3)

  def test_can_retrieve_all_components_for_scan(self):
    components = self.db.getComponentsAllForScan(scan_id=1)
    self.assertIsInstance(components, list)
    self.assertEqual(len(components), 3)
    # ordered by ID
    self.assertEqual(components[0]._id, 1)
    self.assertEqual(components[0].name, "github.com/swinslow/peridot")
    # and includes only components for this scans
    self.assertEqual(components[2]._id, 4)

  def test_cannot_retrieve_all_components_for_scan_without_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      components = self.db.getComponentsAllForScan()

  def test_cannot_retrieve_all_components_for_nonexistent_scan(self):
    with self.assertRaises(ProjectDBQueryError):
      components = self.db.getComponentsAllForScan(scan_id=17)

  def test_can_retrieve_one_component_by_id(self):
    component = self.db.getComponent(_id=2)
    self.assertEqual(component.name, "jQuery")

  def test_can_retrieve_one_component_by_name_and_scan_id(self):
    component = self.db.getComponent(name="spdxLicenseManager", scan_id=1)
    self.assertEqual(component._id, 4)
    component = self.db.getComponent(name="spdxLicenseManager", scan_id=2)
    self.assertEqual(component._id, 3)

  def test_cannot_retrieve_component_by_name_without_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponent(name="jQuery")

  def test_cannot_retrieve_component_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponent(_id=2, name="jQuery")

  def test_cannot_retrieve_component_by_both_id_and_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponent(_id=2, scan_id=1)

  def test_cannot_retrieve_component_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponent()
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponent(scan_id=2)

  def test_cannot_retrieve_component_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getComponent("jQuery")

  def test_returns_none_if_component_not_found_by_id(self):
    component = self.db.getComponent(_id=17)
    self.assertIsNone(component)

  def test_returns_none_if_component_not_found_by_name_and_scan(self):
    component = self.db.getComponent(name="noSuchComponent", scan_id=1)
    self.assertIsNone(component)

  def test_can_add_and_retrieve_components(self):
    component_id = self.db.addComponent(name="github.com/abc/xyz",
      scan_id=2, component_type_id=3)

    # confirm that we now have five components
    components = self.db.getComponentsAll()
    self.assertEqual(len(components), 5)

    # and confirm that we can retrieve this one by id
    component = self.db.getComponent(_id=component_id)
    self.assertEqual(component.name, "github.com/abc/xyz")

    # and confirm that we can retrieve this one by name and scan_id
    component = self.db.getComponent(name="github.com/abc/xyz", scan_id=2)
    self.assertEqual(component._id, component_id)

  def test_can_start_adding_but_rollback_component(self):
    component_id = self.db.addComponent(name="will rollback",
      scan_id=2, component_type_id=1, commit=False)
    self.db.rollback()
    # confirm that we still only have four components
    components = self.db.getComponentsAll()
    self.assertEqual(len(components), 4)
    # and confirm that this component ID doesn't exist in database
    component = self.db.getComponent(_id=component_id)
    self.assertIsNone(component)

  def test_can_start_adding_and_then_commit_components(self):
    c1_id = self.db.addComponent(name="newc1", scan_id=1, component_type_id=1, commit=False)
    c2_id = self.db.addComponent(name="newc2", scan_id=1, component_type_id=1, commit=False)
    self.db.commit()
    # confirm that we now have six component types
    components = self.db.getComponentsAll()
    self.assertEqual(len(components), 6)

  def test_cannot_add_component_with_nonexistent_scan_id(self):
    with self.assertRaises(ProjectDBInsertError):
      c1_id = self.db.addComponent(name="newc1", scan_id=17, component_type_id=1, commit=False)

  def test_cannot_add_component_with_nonexistent_component_type_id(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addComponent(name="newc1", scan_id=1, component_type_id=17, commit=False)

  def test_can_edit_component(self):
    self.db.changeComponent(name="github.com/swinslow/peridot", scan_id=1,
      newName="github.com/swinslow/parascope")
    component = self.db.getComponent(name="github.com/swinslow/parascope", scan_id=1)
    self.assertEqual(component._id, 1)

  def test_cannot_edit_component_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponent(name="invalid", scan_id=1, newName="invalid name")
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponent(name="jQuery", scan_id=17, newName="invalid scan ID")

  def test_cannot_change_component_to_existing_name_in_this_scan(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponent(name="jQuery", scan_id=1, newName="spdxLicenseManager")

  def test_can_change_component_to_existing_name_in_different_scan(self):
    self.db.addComponent(name="newComponent", scan_id=2, component_type_id=3)
    self.db.changeComponent(name="newComponent", scan_id=2, newName="jQuery")
    component = self.db.getComponent(name="jQuery", scan_id=2)
    self.assertEqual(component._id, 5)

  def test_can_change_component_type_id_for_component(self):
    self.db.changeComponent(name="spdxLicenseManager", scan_id=1,
      new_component_type_id=3)
    component = self.db.getComponent(name="spdxLicenseManager", scan_id=1)
    self.assertEqual(component.component_type_id, 3)

  def test_cannot_change_component_to_nonexistent_component_type_id(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponent(name="jQuery", scan_id=1,
        new_component_type_id=17)

  def test_can_change_both_name_and_component_id_at_the_same_time(self):
    self.db.changeComponent(name="spdxLicenseManager", scan_id=1,
      new_component_type_id=3, newName="slm")
    component = self.db.getComponent(name="slm", scan_id=1)
    self.assertEqual(component.component_type_id, 3)

  def test_cannot_change_component_without_something_new(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeComponent(name="jQuery", scan_id=1)
