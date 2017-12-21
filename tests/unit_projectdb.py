# tests/unit_projectdb.py
#
# Unit test for spdxLicenseManager: project database and Config table.
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

import unittest
from unittest import mock

from slm.projectdb import ProjectDB, ProjectDBConfigError

class ProjectDBTestSuite(unittest.TestCase):
  """spdxLicenseManager project database unit test suite."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  # not called by default; only call with each test case function if needed
  def insertSampleData(self):
    # FIXME IMPLEMENT WHEN NEEDED; ALSO CONSIDER BREAKING OUT SUBSETS
    pass

  ##### ProjectDB initialization and closing

  def test_can_create_new_database(self):
    # don't use db from setUp(); create new in-memory DB from scratch
    dbnew = ProjectDB()
    dbnew.createDB(":memory:")
    self.assertTrue(dbnew.isOpened())
    self.assertFalse(dbnew.isInitialized())

  @mock.patch('slm.projectdb.os.path.exists', return_value=True)
  def test_cannot_create_new_database_if_file_already_exists(self, os_exists):
    dbnew = ProjectDB()
    with self.assertRaises(ProjectDBConfigError):
      dbnew.createDB("/tmp/fake/existing.db")

  def test_that_initialized_db_reports_as_initialized(self):
    self.assertTrue(self.db.isInitialized())

  def test_that_closed_db_reports_as_uninitialized(self):
    # don't use db from setUp(); create new in-memory DB from scratch
    dbnew = ProjectDB()
    dbnew.createDB(":memory:")
    # and then close it
    dbnew.closeDB()
    self.assertFalse(dbnew.isInitialized())
    self.assertIsNone(dbnew.session)
    self.assertIsNone(dbnew.engine)
