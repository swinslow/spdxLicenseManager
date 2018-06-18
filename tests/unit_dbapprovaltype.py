# tests/unit_dbapprovaltype.py
#
# Unit test for spdxLicenseManager: database functions for ApprovalTypes.
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

from slm.datatypes import ApprovalType

class DBApprovalTypeUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for approval types in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleApprovalTypeData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleApprovalTypeData(self):
    approval_types = [
      ApprovalType(_id=1, name="GB approval"),
      ApprovalType(_id=2, name="Whitelisted"),
      ApprovalType(_id=3, name="Previously approved"),
    ]
    self.db.session.bulk_save_objects(approval_types)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_approval_types(self):
    approvalTypes = self.db.getApprovalTypesAll()
    self.assertIsInstance(approvalTypes, list)
    self.assertEqual(len(approvalTypes), 3)
    # ordered by ID
    self.assertEqual(approvalTypes[0]._id, 1)
    self.assertEqual(approvalTypes[0].name, "GB approval")

  def test_can_retrieve_one_approval_type_by_id(self):
    approvalType = self.db.getApprovalType(_id=2)
    self.assertEqual(approvalType.name, "Whitelisted")

  def test_can_retrieve_one_approval_type_by_name(self):
    approvalType = self.db.getApprovalType(name="Whitelisted")
    self.assertEqual(approvalType._id, 2)

  def test_cannot_retrieve_approval_type_by_both_name_and_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getApprovalType(_id=3, name="Previously approved")

  def test_cannot_retrieve_approval_type_without_either_name_or_id(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getApprovalType()

  def test_cannot_retrieve_approval_type_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getApprovalType("Whitelisted")

  def test_returns_none_if_approval_type_not_found_by_id(self):
    approvalType = self.db.getApprovalType(_id=17)
    self.assertIsNone(approvalType)

  def test_returns_none_if_approval_type_not_found_by_name(self):
    approvalType = self.db.getApprovalType(name="noSuchType")
    self.assertIsNone(approvalType)

  def test_can_add_and_retrieve_approval_types(self):
    approvalType_id = self.db.addApprovalType(name="TSC approved")

    # confirm that we now have four approval types
    approvalTypes = self.db.getApprovalTypesAll()
    self.assertEqual(len(approvalTypes), 4)

    # and confirm that we can retrieve this one by id
    approvalType = self.db.getApprovalType(_id=4)
    self.assertEqual(approvalType.name, "TSC approved")

    # and confirm that we can retrieve this one by name
    approvalType = self.db.getApprovalType(name="TSC approved")
    self.assertEqual(approvalType._id, 4)

  def test_can_start_adding_but_rollback_approval_type(self):
    approvalType_id = self.db.addApprovalType(name="will rollback",
      commit=False)
    self.db.rollback()
    # confirm that we still only have three approval types
    approvalTypes = self.db.getApprovalTypesAll()
    self.assertEqual(len(approvalTypes), 3)
    # and confirm that this approval type ID doesn't exist in database
    approvalType = self.db.getApprovalType(_id=approvalType_id)
    self.assertIsNone(approvalType)

  def test_can_start_adding_and_then_commit_approval_types(self):
    c1_id = self.db.addApprovalType(name="newc1", commit=False)
    c2_id = self.db.addApprovalType(name="newc2", commit=False)
    self.db.commit()
    # confirm that we now have five approval types
    approvalTypes = self.db.getApprovalTypesAll()
    self.assertEqual(len(approvalTypes), 5)

  def test_can_edit_approval_type(self):
    self.db.changeApprovalTypeName(name="GB approval", newName="GB")
    approvalType = self.db.getApprovalType(name="GB")
    self.assertEqual(approvalType._id, 1)

  def test_cannot_edit_approval_type_that_does_not_exist(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeApprovalTypeName(name="invalid", newName="this will fail")

  def test_cannot_change_approval_type_to_existing_name(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.changeApprovalTypeName(name="GB approval", newName="Whitelisted")
