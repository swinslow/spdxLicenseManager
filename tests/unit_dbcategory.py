# tests/unit_dbcategory.py
#
# Unit test for spdxLicenseManager: database functions for Categories.
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
from testfixtures import TempDirectory

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError)

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

  def test_can_retrieve_one_category_by_id(self):
    category = self.db.getCategory(_id=2)
    self.assertEqual(category.name, "cat of crazy licenses")

  def test_can_retrieve_one_category_by_name(self):
    category = self.db.getCategory(name="a category")
    self.assertEqual(category._id, 1)

  def test_cannot_retrieve_category_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getCategory(_id=3, name="blah category")

  def test_cannot_retrieve_category_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getCategory()

  def test_cannot_retrieve_category_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getCategory("blah category")

  def test_returns_none_if_category_not_found_by_id(self):
    category = self.db.getCategory(_id=17)
    self.assertIsNone(category)

  def test_returns_none_if_category_not_found_by_name(self):
    category = self.db.getCategory(name="noSuchCategory")
    self.assertIsNone(category)

  def test_can_add_and_retrieve_categories(self):
    category_id = self.db.addCategory(name="newcat", order=4)

    # confirm that we now have four categories
    categories = self.db.getCategoriesAll()
    self.assertEqual(len(categories), 4)

    # and confirm that we can retrieve this one by name
    category = self.db.getCategory(name="newcat")
    self.assertEqual(category._id, 4)
    self.assertEqual(category.order, 4)

    # and confirm that we can retrieve this one by id
    category = self.db.getCategory(_id=4)
    self.assertEqual(category.name, "newcat")
    self.assertEqual(category.order, 4)

  def test_can_start_adding_but_rollback_category(self):
    category_id = self.db.addCategory(name="will rollback",
      order=99, commit=False)
    self.db.rollback()
    # confirm that we still only have three categories
    categories = self.db.getCategoriesAll()
    self.assertEqual(len(categories), 3)
    # and confirm that this category ID doesn't exist in database
    category = self.db.getCategory(_id=category_id)
    self.assertIsNone(category)

  def test_can_start_adding_and_then_commit_categories(self):
    c1_id = self.db.addCategory(name="newc1", order=98, commit=False)
    c2_id = self.db.addCategory(name="newc2", order=99, commit=False)
    self.db.commit()
    # confirm that we now have five categories
    categories = self.db.getCategoriesAll()
    self.assertEqual(len(categories), 5)

  def test_omitting_order_from_new_category_places_it_at_end(self):
    category_id = self.db.addCategory(name="newcat")
    category = self.db.getCategory(name="newcat")
    self.assertEqual(category.order, 4)

  def test_cannot_create_category_with_existing_order(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addCategory(name="duplicate order", order=3)

  def test_can_get_highest_category_order(self):
    highestOrder = self.db.getCategoryHighestOrder()
    self.assertEqual(highestOrder, 3)

  def test_highest_order_works_even_with_no_categories(self):
    newdb = ProjectDB()
    newdb.createDB(":memory:")
    newdb.initializeDBTables()
    highestOrder = newdb.getCategoryHighestOrder()
    self.assertEqual(highestOrder, 0)

  def test_can_edit_category_name(self):
    self.db.changeCategoryName(name="a category", newName="another category")
    category = self.db.getCategory(name="another category")
    self.assertEqual(category._id, 1)

  def test_cannot_edit_category_name_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeCategoryName(name="invalid", newName="this will fail")

  def test_cannot_change_category_name_to_existing_name(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeCategoryName(name="a category", newName="blah category")

  def test_can_reorder_categories_from_higher_to_lower(self):
    self.db.changeCategoryOrder(name="a category", sortBefore="blah category")
    categories = self.db.getCategoriesAll()
    self.assertEqual(categories[0].name, "a category")
    self.assertEqual(categories[1].name, "blah category")
    self.assertEqual(categories[2].name, "cat of crazy licenses")

  def test_can_reorder_categories_from_lower_to_higher(self):
    self.db.changeCategoryOrder(name="blah category", sortBefore="a category")
    categories = self.db.getCategoriesAll()
    self.assertEqual(categories[0].name, "cat of crazy licenses")
    self.assertEqual(categories[1].name, "blah category")
    self.assertEqual(categories[2].name, "a category")

  def test_cannot_reorder_category_name_before_one_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeCategoryOrder(name="a category", sortBefore="oops")

  def test_cannot_reorder_category_name_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeCategoryOrder(name="oops", sortBefore="a category")

  def test_cannot_create_category_with_order_less_than_one(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.addCategory(name="need positive order", order=0)
