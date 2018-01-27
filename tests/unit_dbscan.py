# tests/unit_dbscan.py
#
# Unit test for spdxLicenseManager: database functions for Scans.
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
from datetime import datetime

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError)

from slm.datatypes import Scan, Subproject

class DBScanUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for scan metadata in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleSubprojectData()
    self.insertSampleScanData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

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
      Scan(_id=2, subproject_id=3, scan_dt=datetime.date(2017, 1, 3),
        desc="B initial scan"),
      Scan(_id=3, subproject_id=2, scan_dt=datetime.date(2017, 2, 10),
        desc="XYZ 2017-02 monthly scan"),
    ]
    self.db.session.bulk_save_objects(scans)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_scans(self):
    scans = self.db.getScansAll()
    self.assertIsInstance(scans, list)
    self.assertEqual(len(scans), 3)
    # will sort by ID
    self.assertEqual(scans[0]._id, 1)
    self.assertEqual(scans[0].subproject.name, "subX")
    self.assertEqual(scans[1]._id, 2)
    self.assertEqual(scans[1].subproject.name, "subB")
    self.assertEqual(scans[2]._id, 3)
    self.assertEqual(scans[2].subproject.name, "subX")
