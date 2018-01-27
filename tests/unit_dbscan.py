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
import datetime

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
      Scan(_id=2, subproject_id=1, scan_dt=datetime.date(2017, 1, 3),
        desc="1 initial scan"),
      Scan(_id=3, subproject_id=2, scan_dt=datetime.date(2017, 2, 10),
        desc="XYZ 2017-02 monthly scan"),
      Scan(_id=4, subproject_id=2, scan_dt=datetime.date(2017, 2, 17),
        desc="XYZ 2017-02 rescan"),
    ]
    self.db.session.bulk_save_objects(scans)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_all_scans(self):
    scans = self.db.getScansAll()
    self.assertIsInstance(scans, list)
    self.assertEqual(len(scans), 4)
    # will sort by ID
    self.assertEqual(scans[0]._id, 1)
    self.assertEqual(scans[0].subproject.name, "subX")
    self.assertEqual(scans[1]._id, 2)
    self.assertEqual(scans[1].subproject.name, "sub1")
    self.assertEqual(scans[2]._id, 3)
    self.assertEqual(scans[2].subproject.name, "subX")
    self.assertEqual(scans[3]._id, 4)
    self.assertEqual(scans[3].subproject.name, "subX")

  def test_can_retrieve_scans_in_just_one_subproject(self):
    scans = self.db.getScansFiltered(subproject="subX")
    self.assertIsInstance(scans, list)
    self.assertEqual(len(scans), 3)
    # will sort by scan ID
    self.assertEqual(scans[0]._id, 1)
    self.assertEqual(scans[0].desc, "XYZ initial scan")
    self.assertEqual(scans[1]._id, 3)
    self.assertEqual(scans[1].desc, "XYZ 2017-02 monthly scan")
    self.assertEqual(scans[2]._id, 4)
    self.assertEqual(scans[2].desc, "XYZ 2017-02 rescan")

  def test_cannot_retrieve_scans_in_subproject_that_does_not_exist(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getScansFiltered(subproject="invalid")

  def test_can_retrieve_scans_by_subproject_and_month(self):
    scans = self.db.getScansFiltered(subproject="subX", month_tuple=(2017, 2))
    self.assertIsInstance(scans, list)
    self.assertEqual(len(scans), 2)
    # will sort by scan ID
    self.assertEqual(scans[0]._id, 3)
    self.assertEqual(scans[0].desc, "XYZ 2017-02 monthly scan")
    self.assertEqual(scans[1]._id, 4)
    self.assertEqual(scans[1].desc, "XYZ 2017-02 rescan")

  def test_cannot_retrieve_scans_in_subproject_with_integer_month(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getScansFiltered(subproject="subX", month_tuple=2)

  def test_cannot_retrieve_scans_in_subproject_with_invalid_month_tuple(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getScansFiltered(subproject="subX", month_tuple=("hi", "there"))

  def test_retrieve_scan_with_unknown_month_returns_empty_list(self):
    scans = self.db.getScansFiltered(subproject="subX",
      month_tuple=(2017, 3))
    self.assertIsInstance(scans, list)
    self.assertEqual(scans, [])

  def test_can_retrieve_scans_by_month_without_subproject(self):
    scans = self.db.getScansFiltered(month_tuple=(2017, 1))
    self.assertIsInstance(scans, list)
    self.assertEqual(len(scans), 2)
    # will sort by scan ID
    self.assertEqual(scans[0]._id, 1)
    self.assertEqual(scans[0].desc, "XYZ initial scan")
    self.assertEqual(scans[1]._id, 2)
    self.assertEqual(scans[1].desc, "1 initial scan")

  def test_cannot_retrieve_filtered_scans_without_subproject_or_month(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getScansFiltered()

  def test_cannot_retrieve_filtered_scans_with_positional_args(self):
    with self.assertRaises(TypeError):
      self.db.getScansFiltered("subX")
    with self.assertRaises(TypeError):
      self.db.getScansFiltered("subX", (2017, 1))
    with self.assertRaises(TypeError):
      self.db.getScansFiltered((2017, 1))

  def test_can_retrieve_one_scan_by_id(self):
    scan = self.db.getScan(_id=2)
    self.assertEqual(scan.desc, "1 initial scan")

  def test_returns_none_if_scan_not_found_by_id(self):
    scan = self.db.getScan(_id=17)
    self.assertIsNone(scan)

  def test_can_add_and_retrieve_scans(self):
    scan_id = self.db.addScan(subproject="subX", scan_dt_str="2017-03-05",
      desc="XYZ 2017-03 monthly scan")

    # confirm that we now have five scans
    scans = self.db.getScansAll()
    self.assertEqual(len(scans), 5)
    self.assertEqual(scan_id, 5)

    # and confirm that we can retrieve this one by id
    scan = self.db.getScan(_id=5)
    self.assertEqual(scan.desc, "XYZ 2017-03 monthly scan")
    self.assertEqual(scan.subproject.name, "subX")

  def test_can_start_adding_but_rollback_scan(self):
    scan_id = self.db.addScan(subproject="subX", scan_dt_str="2011-01-01",
      desc="will rollback", commit=False)
    self.db.rollback()
    # confirm that we still only have four scans
    scans = self.db.getScansAll()
    self.assertEqual(len(scans), 4)
    # and confirm that this scan ID doesn't exist in database
    scan = self.db.getScan(_id=scan_id)
    self.assertIsNone(scan)

  def test_can_start_adding_and_then_commit_scans(self):
    s1_id = self.db.addScan(subproject="subX", scan_dt_str="2011-01-01",
      desc="s1", commit=False)
    s2_id = self.db.addScan(subproject="subX", scan_dt_str="2012-02-02",
      desc="s2", commit=False)
    self.db.commit()
    # confirm that we now have six scans
    scans = self.db.getScansAll()
    self.assertEqual(len(scans), 6)

  def test_cannot_add_scan_without_subproject(self):
    with self.assertRaises(TypeError):
      self.db.addScan(scan_dt_str="2011-01-01", desc="oops")
    # confirm it wasn't added either
    scan = self.db.getScan(_id=5)
    self.assertIsNone(scan)

  def test_cannot_add_scan_without_scan_date_string(self):
    with self.assertRaises(TypeError):
      self.db.addScan(subproject="subX", desc="oops")
    # confirm it wasn't added either
    scan = self.db.getScan(_id=5)
    self.assertIsNone(scan)

  def test_can_add_scan_with_duplicate_desc(self):
    scan_id = self.db.addScan(subproject="sub1", scan_dt_str="2017-02-02",
      desc="1 initial scan")

    # confirm that we now have five scans and desc matches
    scans = self.db.getScansAll()
    self.assertEqual(len(scans), 5)
    self.assertEqual(scan_id, 5)
    scan = self.db.getScan(_id=5)
    self.assertEqual(scan.desc, "1 initial scan")

  def test_can_add_scan_with_duplicate_scan_date(self):
    scan_id = self.db.addScan(subproject="sub1", scan_dt_str="2017-01-03",
      desc="1 rescan")

    # confirm that we now have five scans and desc matches
    scans = self.db.getScansAll()
    self.assertEqual(len(scans), 5)
    self.assertEqual(scan_id, 5)
    scan = self.db.getScan(_id=5)
    self.assertEqual(scan.desc, "1 rescan")
