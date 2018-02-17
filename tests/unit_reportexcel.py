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
from collections import OrderedDict
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

   # create reporter
    self.reporter = ExcelReporter()

  def tearDown(self):
    pass

  ##### Test helpers to mimic results from analysis

  def _buildCategories(self, results):
    self.cat2 = Category()
    self.cat2._id = 2
    self.cat2.name = "catID2"
    self.cat2.order = 1
    self.cat2.licensesSorted = OrderedDict()
    self.cat2.hasFiles = True
    results[2] = self.cat2

    # no files, cat3 should not appear in reports
    self.cat3 = Category()
    self.cat3._id = 3
    self.cat3.name = "catID3"
    self.cat3.order = 2
    self.cat3.licensesSorted = OrderedDict()
    self.cat3.hasFiles = False
    results[3] = self.cat3

    self.cat1 = Category()
    self.cat1._id = 1
    self.cat1.name = "catID1"
    self.cat1.order = 3
    self.cat1.licensesSorted = OrderedDict()
    self.cat1.hasFiles = True
    results[1] = self.cat1

  def _buildLicenses(self, results):
    # should sort alphabetically before lic1cat2 in reports
    self.lic2cat2 = License()
    self.lic2cat2._id = 2
    self.lic2cat2.name = "another lic2cat2"
    self.lic2cat2.category_id = 2
    self.lic2cat2.filesSorted = OrderedDict()
    self.lic2cat2.hasFiles = True
    self.cat2.licensesSorted[2] = self.lic2cat2

    self.lic1cat2 = License()
    self.lic1cat2._id = 1
    self.lic1cat2.name = "lic1cat2"
    self.lic1cat2.category_id = 2
    self.lic1cat2.filesSorted = OrderedDict()
    self.lic1cat2.hasFiles = True
    self.cat2.licensesSorted[1] = self.lic1cat2

    # no files, lic3cat2 should not appear in reports
    self.lic3cat2 = License()
    self.lic3cat2._id = 3
    self.lic3cat2.name = "nope lic3cat2"
    self.lic3cat2.category_id = 2
    self.lic3cat2.filesSorted = OrderedDict()
    self.lic3cat2.hasFiles = False
    self.cat2.licensesSorted[3] = self.lic3cat2

    # no files, lic4cat3 should not appear in reports
    self.lic4cat3 = License()
    self.lic4cat3._id = 4
    self.lic4cat3.name = "nope lic4cat3"
    self.lic4cat3.category_id = 3
    self.lic4cat3.filesSorted = OrderedDict()
    self.lic4cat3.hasFiles = False
    self.cat3.licensesSorted[4] = self.lic4cat3

    self.lic5cat1 = License()
    self.lic5cat1._id = 5
    self.lic5cat1.name = "a license"
    self.lic5cat1.category_id = 1
    self.lic5cat1.filesSorted = OrderedDict()
    self.lic5cat1.hasFiles = True
    self.cat1.licensesSorted[5] = self.lic5cat1

  def _buildFiles(self, results):
    # should sort alphabetically by path before f1
    self.f2 = File()
    self.f2._id = 2
    self.f2.path = "/first/tmp/f2"
    self.f2.scan_id = 1
    self.f2.license_id = 2
    self.f2.findings = {}
    self.lic2cat2.filesSorted[2] = self.f2

    self.f1 = File()
    self.f1._id = 1
    self.f1.path = "/tmp/f1"
    self.f1.scan_id = 1
    self.f1.license_id = 2
    self.f1.findings = {}
    self.lic2cat2.filesSorted[1] = self.f1

    # should sort after f2 and f1 b/c license ID sorts after theirs
    self.f3 = File()
    self.f3._id = 3
    self.f3.path = "/earliest/tmp/f3"
    self.f3.scan_id = 1
    self.f3.license_id = 1
    self.f3.findings = {}
    self.lic1cat2.filesSorted[3] = self.f3

    self.f4 = File()
    self.f4._id = 4
    self.f4.path = "/tmp/f4"
    self.f4.scan_id = 1
    self.f4.license_id = 1
    self.f4.findings = {}
    self.lic1cat2.filesSorted[4] = self.f4

    self.f5 = File()
    self.f5._id = 5
    self.f5.path = "/tmp/f5"
    self.f5.scan_id = 1
    self.f5.license_id = 5
    self.f5.findings = {}
    self.lic5cat1.filesSorted[5] = self.f5

  def _getAnalysisResults(self):
    results = OrderedDict()
    self._buildCategories(results)
    self._buildLicenses(results)
    self._buildFiles(results)
    return results

  ##### Test cases below

  def test_new_reporter_is_in_reset_state(self):
    self.assertIsNone(self.reporter.results)
    self.assertIsNone(self.reporter.wb)
    self.assertFalse(self.reporter.reportGenerated)

  ##### Reporter setup function tests

  def test_can_set_results_and_create_workbook(self):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.assertEqual(Workbook, type(self.reporter.wb))
    self.assertEqual(results, self.reporter.results)

  ##### Reporter generate function tests

  def test_generate_report_fails_if_results_not_ready(self):
    with self.assertRaises(ReportNotReadyError):
      self.reporter.generate()
    self.assertFalse(self.reporter.reportGenerated)

    # even with workbook created, should fail if results aren't ready yet
    self.reporter.wb = Workbook()
    with self.assertRaises(ReportNotReadyError):
      self.reporter.generate()
    self.assertFalse(self.reporter.reportGenerated)

  @mock.patch('slm.reports.xlsx.ExcelReporter._generateFileListings')
  @mock.patch('slm.reports.xlsx.ExcelReporter._generateCategorySheets')
  def test_generate_calls_required_helpers(self, cs_mock, file_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()
    cs_mock.assert_called_with(self.reporter.wb, self.reporter.results)
    file_mock.assert_called_with(self.reporter.wb, self.reporter.results)

  def test_generate_sets_report_generated_flag(self):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()
    self.assertTrue(self.reporter.reportGenerated)

  def test_can_generate_report_category_pages(self):
    wb = Workbook()
    results = self._getAnalysisResults()
    self.reporter._generateCategorySheets(wb, results)

    # workbook now has the expected category sheets
    # catID3 does not appear because it has no files
    self.assertEqual(["catID2", "catID1"], wb.sheetnames)
    # proper headers are set for each category page
    for sheet in wb:
      self.assertEqual("File", sheet['A1'].value)
      self.assertEqual("License", sheet['B1'].value)

  def test_cannot_generate_files_before_category_sheets_are_generated(self):
    wb = Workbook()
    results = self._getAnalysisResults()
    with self.assertRaises(ReportNotReadyError):
      self.reporter._generateFileListings(wb, results)

  def test_can_generate_file_listings(self):
    wb = Workbook()
    results = self._getAnalysisResults()
    self.reporter._generateCategorySheets(wb, results)
    self.reporter._generateFileListings(wb, results)

    # correct files and licenses are in the correct cells
    ws1 = wb['catID2']
    self.assertEqual("/first/tmp/f2", ws1['A2'].value)
    self.assertEqual("another lic2cat2", ws1['B2'].value)
    self.assertEqual("/tmp/f1", ws1['A3'].value)
    self.assertEqual("another lic2cat2", ws1['B3'].value)
    self.assertEqual("/earliest/tmp/f3", ws1['A4'].value)
    self.assertEqual("lic1cat2", ws1['B4'].value)
    self.assertEqual("/tmp/f4", ws1['A5'].value)
    self.assertEqual("lic1cat2", ws1['B5'].value)

    ws2 = wb['catID1']
    self.assertEqual("/tmp/f5", ws2['A2'].value)
    self.assertEqual("a license", ws2['B2'].value)

  ##### Reporter save function tests

  @mock.patch('slm.reports.xlsx.os.path.exists', return_value=True)
  def test_save_check_raises_exception_if_file_already_exists(self, os_exists):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()

    with self.assertRaises(ReportFileError):
      self.reporter._saveCheck(path="/tmp/fake/existing.xlsx")

  @mock.patch('slm.reports.xlsx.os.path.exists', return_value=True)
  @mock.patch('slm.reports.xlsx.os.access', return_value=True)
  def test_save_check_doesnt_raise_exception_if_replace_flag_set(self, os_access, os_exists):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()

    try:
      self.reporter._saveCheck(path="/tmp/fake/existing.xlsx", replace=True)
    except ReportFileError:
      self.fail("ReportFileError raised even though replace flag is True")

  @mock.patch('slm.reports.xlsx.os.access', return_value=False)
  def test_save_check_fails_if_no_write_permission_for_path(self, os_access):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()

    with self.assertRaises(ReportFileError):
      self.reporter._saveCheck(path="/tmp/readonly/report.xlsx")

  def test_save_check_fails_if_report_not_ready_yet(self):
    with self.assertRaises(ReportNotReadyError):
      self.reporter._saveCheck(path="whatever")

    # and even with results added, should fail if report not generated yet
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    with self.assertRaises(ReportNotReadyError):
      self.reporter._saveCheck(path="whatever")

  @mock.patch('slm.reports.xlsx.openpyxl.workbook.Workbook.save')
  @mock.patch('slm.reports.xlsx.ExcelReporter._saveCheck')
  def test_save_calls_save_checker(self, check_mock, save_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.generate()

    path = "something"
    replace = True
    self.reporter.save(path=path, replace=replace)
    check_mock.assert_called_with(path=path, replace=replace)
    save_mock.assert_called_with(path)
