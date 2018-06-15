# tests/unit_dbcomponentlicense.py
#
# Unit test for spdxLicenseManager: database functions for ComponentLicenses.
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

from slm.datatypes import (Category, Component, ComponentLicense,
  ComponentType, File, License, Scan, Subproject)

class DBComponentLicenseUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for component licenses in DB."""

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
    self.insertSampleComponentLicenseData()

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
      License(_id=5, name="Apache-2.0", category_id=3),
      License(_id=6, name="CC-BY-4.0", category_id=3),
      License(_id=7, name="CC0-1.0", category_id=2),
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

  def insertSampleComponentLicenseData(self):
    clics = [
      ComponentLicense(component_id=4, license_id=5),
      ComponentLicense(component_id=4, license_id=6),
      ComponentLicense(component_id=3, license_id=5),
      ComponentLicense(component_id=3, license_id=6),
      ComponentLicense(component_id=3, license_id=7),
    ]
    self.db.session.bulk_save_objects(clics)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_licenses_for_component_id(self):
    lics = self.db.getComponentLicenses(component_id=3)
    self.assertIsInstance(lics, list)
    self.assertEqual(len(lics), 3)
    self.assertIsInstance(lics[0], License)
    self.assertEqual(lics[0]._id, 5)
    self.assertEqual(lics[0].name, "Apache-2.0")

  def test_cannot_retrieve_all_licenses_without_args(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses()

  def test_cannot_retrieve_all_licenses_with_invalid_component_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(component_id=17)

  def test_cannot_retrieve_all_licenses_with_component_id_and_name(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(component_id=3, name="spdxLicenseManager")

  def test_cannot_retrieve_all_licenses_with_component_id_and_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(component_id=3, scan_id=2)

  def test_cannot_retrieve_all_licenses_with_invalid_component_name(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(name="blah", scan_id=1)

  def test_cannot_retrieve_all_licenses_with_invalid_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(name="spdxLicenseManager", scan_id=17)

  def test_cannot_retrieve_all_licenses_with_component_name_but_without_scan_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getComponentLicenses(name="jQuery")

  def test_retrieve_returns_empty_list_for_no_component_licenses(self):
    lics = self.db.getComponentLicenses(component_id=1)
    self.assertEqual(lics, [])

  def test_can_retrieve_all_licenses_for_component_name_and_scan_id(self):
    lics = self.db.getComponentLicenses(name="spdxLicenseManager", scan_id=2)
    self.assertIsInstance(lics, list)
    self.assertEqual(len(lics), 3)
    self.assertIsInstance(lics[0], License)
    self.assertEqual(lics[0]._id, 5)
    self.assertEqual(lics[0].name, "Apache-2.0")

  def test_can_add_license_to_component(self):
    self.db.addComponentLicense(component_id=2, license_id=2)
    lics = self.db.getComponentLicenses(component_id=2)
    self.assertEqual(len(lics), 1)
    self.assertEqual(lics[0]._id, 2)
    self.assertEqual(lics[0].name, "HarshEULA")

  def test_can_start_adding_but_rollback_component_license(self):
    self.db.addComponentLicense(component_id=3, license_id=2, commit=False)
    self.db.rollback()
    # confirm that component 3 still only has 3 licenses
    lics = self.db.getComponentLicenses(component_id=3)
    self.assertEqual(len(lics), 3)
    # and confirm that this component's license isn't in the list
    for lic in lics:
      self.assertNotEqual(lic._id, 2)

  def test_can_start_adding_and_then_commit_component_licenses(self):
    self.db.addComponentLicense(component_id=3, license_id=2, commit=False)
    self.db.addComponentLicense(component_id=3, license_id=1, commit=False)
    self.db.commit()
    # confirm that component 3 now has 5 licenses
    lics = self.db.getComponentLicenses(component_id=3)
    self.assertEqual(len(lics), 5)

  def test_cannot_add_component_license_to_nonexistent_component(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addComponentLicense(component_id=17, license_id=2)

  def test_cannot_add_component_license_with_nonexistent_license(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addComponentLicense(component_id=2, license_id=17)
