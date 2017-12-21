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

from slm.projectdb import ProjectDB

class ProjectDBTestSuite(unittest.TestCase):
  """spdxLicenseManager project database unit test suite."""

  def setUp(self):
    # create and initialize an in-memory database
    #self.db = ProjectDB()
    #self.db.createDatabase(":memory:")
    #self.db.initializeDatabaseTables()
    pass

  def tearDown(self):
    self.db.closeDatabase()
    self.db = None

  # not called by default; only call with each test case function if needed
  def insertSampleData(self):
    # FIXME IMPLEMENT WHEN NEEDED; ALSO CONSIDER BREAKING OUT SUBSETS
    pass

  ##### ProjectDB object initialization and closing

  def test_can_create_new_database(self):
    # don't use db from setUp(); create new in-memory DB from scratch
    self.dbnew = ProjectDB()
    self.dbnew.createDatabase(":memory:")
    self.assertTrue(self.dbnew.isOpened())
    self.assertFalse(self.dbnew.isInitialized())
