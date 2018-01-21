# tests/unit_dbconversion.py
#
# Unit test for spdxLicenseManager: database functions for Conversions.
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

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError, ProjectDBDeleteError)

from slm.datatypes import Category, Conversion, License

class DBConversionUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for converting license names in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()
    self.insertSampleLicenseData()
    self.insertSampleConversionData()

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

  def insertSampleConversionData(self):
    conversions = [
      Conversion(_id=1, old_text="293", new_license_id=3),
      Conversion(_id=2, old_text="NC", new_license_id=4),
      Conversion(_id=3, old_text="anything", new_license_id=1),
    ]
    self.db.session.bulk_save_objects(conversions)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_one_conversion_by_id(self):
    conversion = self.db.getConversion(_id=2)
    self.assertEqual(conversion.old_text, "NC")
    self.assertEqual(conversion.new_license_id, 4)
    self.assertEqual(conversion.new_license._id, 4)
    self.assertEqual(conversion.new_license.name, "DoAnythingNoncommercial")

  def test_can_retrieve_one_conversion_by_name(self):
    conversion = self.db.getConversion(old_text="293")
    self.assertEqual(conversion._id, 1)

  def test_cannot_retrieve_conversion_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getConversion(_id=3, old_text="anything")

  def test_cannot_retrieve_conversion_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getConversion()

  def test_cannot_retrieve_conversion_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getConversion("NC")

  def test_returns_none_if_conversion_not_found_by_id(self):
    conversion = self.db.getConversion(_id=17)
    self.assertIsNone(conversion)

  def test_returns_none_if_conversion_not_found_by_name(self):
    conversion = self.db.getConversion(old_text="noSuchConversion")
    self.assertIsNone(conversion)
