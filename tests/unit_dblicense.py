# tests/unit_dblicense.py
#
# Unit test for spdxLicenseManager: database functions for Licenses.
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

import os
import unittest
from unittest import mock
from testfixtures import TempDirectory

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError)

from slm.datatypes import Category, License

class DBLicenseUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for license data in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()
    self.insertSampleLicenseData()

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

  ##### Test cases below

  def test_can_retrieve_all_license_names(self):
    licenses = self.db.getLicensesAll()
    self.assertIsInstance(licenses, list)
    self.assertEqual(len(licenses), 4)
    # will sort alphabetically
    self.assertEqual(licenses[0]._id, 3)
    self.assertEqual(licenses[0].name, "293PageEULA")

  def test_can_retrieve_one_license_by_id(self):
    license = self.db.getLicense(_id=2)
    self.assertEqual(license.name, "HarshEULA")

  def test_can_retrieve_one_license_by_name(self):
    license = self.db.getLicense(name="DoAnything")
    self.assertEqual(license._id, 1)

  def test_cannot_retrieve_license_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getLicense(_id=3, name="293PageEULA")

  def test_cannot_retrieve_license_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getLicense()

  def test_cannot_retrieve_license_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getLicense("DoAnything")

  def test_returns_none_if_license_not_found_by_id(self):
    license = self.db.getLicense(_id=17)
    self.assertIsNone(license)

  def test_returns_none_if_license_not_found_by_name(self):
    license = self.db.getLicense(name="noSuchLicense")
    self.assertIsNone(license)

  def test_can_add_and_retrieve_licenses(self):
    license_id = self.db.addLicense(name="SomeOtherEULA",
      category="blah category")

    # confirm that we now have five licenses
    licenses = self.db.getLicensesAll()
    self.assertEqual(len(licenses), 5)

    # and confirm that we can retrieve this one by name
    license = self.db.getLicense(name="SomeOtherEULA")
    self.assertEqual(license._id, 5)
    self.assertEqual(license.category_id, 3)
    self.assertIsNotNone(license.category)
    self.assertEqual(license.category.name, "blah category")

    # and confirm that we can retrieve this one by id
    license = self.db.getLicense(_id=5)
    self.assertEqual(license.name, "SomeOtherEULA")
    self.assertEqual(license.category_id, 3)

  def test_can_start_adding_but_rollback_license(self):
    license_id = self.db.addLicense(name="will rollback",
      category="blah category", commit=False)
    self.db.rollback()
    # confirm that we still only have four licenses
    licenses = self.db.getLicensesAll()
    self.assertEqual(len(licenses), 4)
    # and confirm that this license ID doesn't exist in database
    license = self.db.getLicense(_id=license_id)
    self.assertIsNone(license)

  def test_can_start_adding_and_then_commit_licenses(self):
    l1_id = self.db.addLicense(name="newl1", category="cat", commit=False)
    l2_id = self.db.addLicense(name="newl2", category="cat", commit=False)
    self.db.commit()
    # confirm that we now have six licenses
    licenses = self.db.getLicensesAll()
    self.assertEqual(len(licenses), 6)

  def test_cannot_add_license_without_category(self):
    with self.assertRaises(TypeError):
      self.db.addLicense(name="oops")
    # confirm it wasn't added either
    license = self.db.getLicense(name="oops")
    self.assertIsNone(license)

  def test_cannot_add_license_without_existing_category(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addLicense(name="oops", category="noSuchCategory")
    # confirm it wasn't added either
    license = self.db.getLicense(name="oops")
    self.assertIsNone(license)

  def test_cannot_add_license_with_duplicate_name(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addLicense(name="DoAnything", category="cat")
