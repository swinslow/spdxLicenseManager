# tests/unit_slmmanager.py
#
# Unit test for spdxLicenseManager: top-level SLM manager.
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

import unittest
import datetime

from unittest import mock

from slm.slmmanager import SLMManager, SLMManagerError
from slm.slmconfig import SLMConfig
from slm.datatypes import Scan, Subproject
from slm.projectdb import ProjectDB

class SLMManagerTestSuite(unittest.TestCase):
  """spdxLicenseManager SLM manager unit test suite."""

  def setUp(self):
    # fake SLM config
    mainconfig_json = """{
      "projects": [
        { "name": "frotz", "desc": "The FROTZ Project" },
        { "name": "rezrov", "desc": "The REZROV Project" },
        { "name": "gnusto", "desc": "The GNUSTO Project" }
      ]
    }"""
    self.mainconfig = SLMConfig()
    self.mainconfig.loadConfig(mainconfig_json)

    # SLM manager for testing
    self.manager = SLMManager(config=self.mainconfig, root="/tmp/fake/whatever")

    # fake DBs for projects
    self.frotz_db = ProjectDB()
    self.frotz_db.createDB(":memory:")
    self.frotz_db.initializeDBTables()

    self.rezrov_db = ProjectDB()
    self.rezrov_db.createDB(":memory:")
    self.rezrov_db.initializeDBTables()

    self.gnusto_db = ProjectDB()
    self.gnusto_db.createDB(":memory:")
    self.gnusto_db.initializeDBTables()

    # insert sample data
    self.insertSampleSubprojectData()
    self.insertSampleScans()

  def tearDown(self):
    pass

  def insertSampleSubprojectData(self):
    # for frotz
    frotz_subprojects = [
      Subproject(_id=1, name="f1", spdx_search="f1", desc="subproject f1"),
      Subproject(_id=2, name="f2", spdx_search="fX2", desc="subproject fX2"),
      Subproject(_id=3, name="f3", spdx_search="f3", desc="f3"),
    ]
    self.frotz_db.session.bulk_save_objects(frotz_subprojects)
    self.frotz_db.session.commit()

    # for gnusto
    # note that IDs restart b/c projects keep separate databases
    gnusto_subprojects = [
      Subproject(_id=1, name="g1", spdx_search="g1", desc="subproject g1"),
      Subproject(_id=2, name="g2", spdx_search="gAX2", desc="gAX2"),
    ]
    self.gnusto_db.session.bulk_save_objects(gnusto_subprojects)
    self.gnusto_db.session.commit()

    # none for rezrov

  def insertSampleScans(self):
    # for frotz
    frotz_scans = [
      Scan(_id=1, subproject_id=2, scan_dt=datetime.date(2017, 1, 10),
        desc="fX2 initial scan"),
      Scan(_id=2, subproject_id=1, scan_dt=datetime.date(2017, 2, 3),
        desc="f1 initial scan"),
      Scan(_id=3, subproject_id=2, scan_dt=datetime.date(2017, 2, 10),
        desc="fX2 2017-02 monthly scan"),
      Scan(_id=4, subproject_id=2, scan_dt=datetime.date(2017, 2, 17),
        desc="fX2 2017-02 rescan"),
      # none for subproject 3
    ]
    self.frotz_db.session.bulk_save_objects(frotz_scans)
    self.frotz_db.session.commit()

    # for gnusto
    # note that IDs restart b/c projects keep separate databases
    gnusto_scans = [
      # none for subproject 1
      Scan(_id=1, subproject_id=2, scan_dt=datetime.date(2017, 1, 10),
        desc="gAX2 initial scan"),
      Scan(_id=2, subproject_id=2, scan_dt=datetime.date(2017, 2, 3),
        desc="gAX2 2017-02 monthly scan"),
    ]
    self.gnusto_db.session.bulk_save_objects(gnusto_scans)
    self.gnusto_db.session.commit()

    # none for rezrov

  ##### Test cases below

  def test_can_get_list_of_all_projects(self):
    projects = self.manager.getProjects()
    self.assertIsInstance(projects, list)
    self.assertEqual(len(projects), 3)
    self.assertIn("frotz", projects)
    self.assertIn("gnusto", projects)
    self.assertIn("rezrov", projects)

  def test_can_get_project_directory_path(self):
    frotz_dir = self.manager.getProjectDir("frotz")
    self.assertEqual(frotz_dir, "/tmp/fake/whatever/projects/frotz")

  def test_can_get_project_database_path(self):
    frotz_db_path = self.manager.getProjectDBPath("frotz")
    self.assertEqual(frotz_db_path, "/tmp/fake/whatever/projects/frotz/frotz.db")

  def test_can_get_project_reports_directory_path(self):
    frotz_reports_dir = self.manager.getProjectReportsDir("frotz")
    self.assertEqual(frotz_reports_dir, "/tmp/fake/whatever/projects/frotz/reports")

  def test_can_get_subprojects_directory_path(self):
    f2_dir = self.manager.getSubprojectDir("frotz", "f2")
    self.assertEqual(f2_dir, "/tmp/fake/whatever/projects/frotz/subprojects/f2")

  def test_can_get_subprojects_reports_directory_path(self):
    f2_reports_dir = self.manager.getSubprojectReportsDir("frotz", "f2")
    self.assertEqual(f2_reports_dir, "/tmp/fake/whatever/projects/frotz/subprojects/f2/reports")

  def test_can_get_subprojects_spdx_directory_path(self):
    f2_spdx_dir = self.manager.getSubprojectSPDXDir("frotz", "f2")
    self.assertEqual(f2_spdx_dir, "/tmp/fake/whatever/projects/frotz/subprojects/f2/spdx")

  def test_can_get_subproject_scan_dates_for_month_with_one_scan(self):
    dates = self.manager.getScanDates(self.frotz_db, "f1", "2017-02")
    self.assertIsInstance(dates, list)
    self.assertEqual(len(dates), 1)
    self.assertEqual(dates[0], "2017-02-03")

  def test_can_get_subproject_scan_dates_for_month_with_two_scans(self):
    dates = self.manager.getScanDates(self.frotz_db, "f2", "2017-02")
    self.assertIsInstance(dates, list)
    self.assertEqual(len(dates), 2)
    self.assertEqual(dates[0], "2017-02-10")
    self.assertEqual(dates[1], "2017-02-17")

  def test_getting_scan_dates_without_scans_returns_empty_list(self):
    dates = self.manager.getScanDates(self.frotz_db, "f3", "2017-02")
    self.assertIsInstance(dates, list)
    self.assertEqual(len(dates), 0)

  def test_getting_scan_dates_without_choosing_subproject_raises_exception(self):
    with self.assertRaises(SLMManagerError):
      self.manager.getScanDates(self.frotz_db, None, "2017-02")

  def test_getting_scan_dates_without_any_subprojects_raises_exception(self):
    with self.assertRaises(SLMManagerError):
      self.manager.getScanDates(self.rezrov_db, None, "2017-02")

  def test_getting_scan_dates_with_nonexistent_subproject_raises_exception(self):
    with self.assertRaises(SLMManagerError):
      self.manager.getScanDates(self.frotz_db, "oops", "2017-02")

  def test_can_check_if_any_scan_is_present_for_given_month(self):
    retval = self.manager.isScanForMonth(self.frotz_db, "f1", "2017-02")
    self.assertTrue(retval)
    retval = self.manager.isScanForMonth(self.frotz_db, "f2", "2017-02")
    self.assertTrue(retval)
    retval = self.manager.isScanForMonth(self.frotz_db, "f3", "2017-02")
    self.assertFalse(retval)

  def test_can_get_spdx_possible_filenames_for_scan_dt(self):
    spdx_paths = self.manager.getSPDXExpectedPaths(self.frotz_db, "frotz", "f1", "2017-02")
    self.assertIsInstance(spdx_paths, list)
    self.assertEqual(len(spdx_paths), 1)
    self.assertEqual(spdx_paths[0],
      "/tmp/fake/whatever/projects/frotz/subprojects/f1/spdx/f1-2017-02-03.spdx")

    spdx_paths2 = self.manager.getSPDXExpectedPaths(self.frotz_db, "frotz", "f2", "2017-02")
    self.assertIsInstance(spdx_paths2, list)
    self.assertEqual(len(spdx_paths2), 2)
    self.assertEqual(spdx_paths2[0],
      "/tmp/fake/whatever/projects/frotz/subprojects/f2/spdx/f2-2017-02-10.spdx")
    self.assertEqual(spdx_paths2[1],
      "/tmp/fake/whatever/projects/frotz/subprojects/f2/spdx/f2-2017-02-17.spdx")

  @mock.patch('slm.projectdb.os.path.isfile', return_value=True)
  def test_can_check_if_spdx_file_is_present(self, os_isfile):
    retval = self.manager.isSPDXForMonth(self.frotz_db, "frotz", "f1", "2017-02")
    self.assertTrue(retval)

  @mock.patch('slm.projectdb.os.path.isfile', return_value=False)
  def test_can_check_if_spdx_file_is_absent(self, os_isfile):
    retval = self.manager.isSPDXForMonth(self.frotz_db, "frotz", "f1", "2017-02")
    self.assertFalse(retval)

  @mock.patch('slm.projectdb.os.path.isfile', return_value=True)
  def test_can_check_if_xlsx_report_is_present(self, os_isfile):
    retval = self.manager.isXLSXForMonth("frotz", "f1", "2017-02")
    self.assertTrue(retval)

  @mock.patch('slm.projectdb.os.path.isfile', return_value=False)
  def test_can_check_if_xlsx_report_is_absent(self, os_isfile):
    retval = self.manager.isXLSXForMonth("frotz", "f1", "2017-02")
    self.assertFalse(retval)

  @mock.patch('slm.projectdb.os.path.isfile', return_value=True)
  def test_can_check_if_json_report_is_present(self, os_isfile):
    retval = self.manager.isJSONForMonth("frotz", "f1", "2017-02")
    self.assertTrue(retval)

  @mock.patch('slm.projectdb.os.path.isfile', return_value=False)
  def test_can_check_if_json_report_is_absent(self, os_isfile):
    retval = self.manager.isJSONForMonth("frotz", "f1", "2017-02")
    self.assertFalse(retval)
