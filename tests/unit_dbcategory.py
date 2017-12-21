# tests/unit_dbcategory.py
#
# Unit test for spdxLicenseManager: database functions for Categories.
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

from slm.projectdb import ProjectDB
from slm.datatypes import Category

class DBCategoryUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for category data in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleCategoryData(self):
    categories = [
      Category(_id=1, name="a category", order=3),
      Category(_id=2, name="cat of crazy licenses", order=2),
      Category(_id=3, name="blah category", order=1),
    ]
    self.db.session.bulk_save_objects(categories)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_category_names_and_descs(self):
    categories = self.db.getCategoriesAll()
    self.assertIsInstance(categories, list)
    self.assertEqual(len(categories), 3)
    self.assertEqual(categories[0]._id, 3)
    self.assertEqual(categories[0].name, "blah category")
    self.assertEqual(categories[0].order, 1)

  def test_all_categories_are_sorted_by_order(self):
    categories = self.db.getCategoriesAll()
    self.assertEqual(categories[0].name, "blah category")
    self.assertEqual(categories[1].name, "cat of crazy licenses")
    self.assertEqual(categories[2].name, "a category")
