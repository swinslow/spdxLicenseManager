# tests/unit_reportexcel.py
#
# Unit test for spdxLicenseManager: creating Excel reports.
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

from openpyxl import Workbook

from slm.datatypes import Category, File, License, Scan, Subproject
from slm.projectdb import ProjectDB, ProjectDBQueryError
from slm.reports.common import ReportFileError, ReportNotReadyError
from slm.reports.xlsx import ExcelReporter

class ReportExcelTestSuite(unittest.TestCase):
  """spdxLicenseManager Excel reporting unit test suite."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()
    self.insertSampleLicenseData()
    self.insertSampleSubprojectData()
    self.insertSampleScanData()
    self.insertSampleFileData()

    # create reporter
    self.reporter = ExcelReporter()

  def tearDown(self):
    pass

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

  def insertSampleSubprojectData(self):
    subprojects = [
      Subproject(_id=1, name="sub1", desc="subproject 1"),
    ]
    self.db.session.bulk_save_objects(subprojects)
    self.db.session.commit()

  def insertSampleScanData(self):
    scans = [
      Scan(_id=1, subproject_id=1, scan_dt=datetime.date(2017, 1, 10),
        desc="new scan"),
    ]
    self.db.session.bulk_save_objects(scans)
    self.db.session.commit()
    self.scan_id = 1

  def insertSampleFileData(self):
    files = [
      File(_id=1, scan_id=1, license_id=1, path="/tmp/f1", sha1=None, md5="abcdef", sha256=None),
      File(_id=2, scan_id=1, license_id=4, path="/tmp/f2", sha1=None, md5=None, sha256="abcdef"),
      File(_id=3, scan_id=1, license_id=2, path="/tmp/f3", sha1="abcdef", md5=None, sha256=None),
      File(_id=4, scan_id=1, license_id=2, path="/tmp/f4", sha1=None, md5=None, sha256=None),
    ]
    self.db.session.bulk_save_objects(files)
    self.db.session.commit()

  ##### Test cases below

  def test_new_reporter_is_in_reset_state(self):
    self.assertFalse(self.reporter.isReady)
    self.assertIsNone(self.reporter.wb)

  @mock.patch('slm.reports.xlsx.os.path.exists', return_value=True)
  def test_save_raises_exception_if_file_already_exists(self, os_exists):
    # fake that the report is ready
    self.reporter.wb = Workbook()
    self.reporter.isReady = True

    with self.assertRaises(ReportFileError):
      self.reporter.save(path="/tmp/fake/existing.xlsx")

  @mock.patch('slm.reports.xlsx.os.path.exists', return_value=True)
  def test_save_doesnt_raise_exception_if_replace_flag_set(self, os_exists):
    # fake that the report is ready
    self.reporter.wb = Workbook()
    self.reporter.isReady = True

    try:
      self.reporter.save(path="/tmp/fake/existing.xlsx", replace=True)
    except ReportFileError:
      self.fail("ReportFileError raised even though replace flag is True")

  @mock.patch('slm.reports.xlsx.openpyxl.writer.excel.save_workbook')
  def test_save_fails_if_no_write_permission_for_path(self, save_mock):
    # fake that the report is ready
    self.reporter.wb = Workbook()
    self.reporter.isReady = True

    save_mock.side_effect = PermissionError
    with self.assertRaises(ReportFileError):
      self.reporter.save(path="/tmp/readonly/report.xlsx")

  def test_save_fails_if_report_not_ready_yet(self):
    newReporter = ExcelReporter()
    with self.assertRaises(ReportNotReadyError):
      newReporter.save(path="whatever")
