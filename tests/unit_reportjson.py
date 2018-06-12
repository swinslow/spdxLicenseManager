# tests/unit_reportjson.py
#
# Unit test for spdxLicenseManager: creating json reports.
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
import json

from slm.datatypes import Category, File, License, Scan, Subproject
from slm.projectdb import ProjectDB, ProjectDBQueryError
from slm.reports.common import ReportFileError, ReportNotReadyError
from slm.reports.json import JSONReporter

class ReportJSONTestSuite(unittest.TestCase):
  """spdxLicenseManager JSON reporting unit test suite."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

   # create reporter
    self.reporter = JSONReporter(db=self.db)

  def tearDown(self):
    pass

  ##### Test helpers to mimic results from analysis

  def _buildCategories(self, results):
    self.cat2 = Category()
    self.cat2._id = 2
    self.cat2.name = "catID2"
    self.cat2.licenses = []
    results.append(self.cat2)

    self.cat1 = Category()
    self.cat1._id = 1
    self.cat1.name = "catID1"
    self.cat1.licenses = []
    results.append(self.cat1)

    self.cat4 = Category()
    self.cat4._id = 4
    self.cat4.name = "No license found"
    self.cat4.licenses = []
    results.append(self.cat4)

  def _buildLicenses(self, results):
    # should sort alphabetically before lic1cat2 in reports
    self.lic2cat2 = License()
    self.lic2cat2._id = 2
    self.lic2cat2.name = "another lic2cat2"
    self.lic2cat2.files = []
    self.cat2.licenses.append(self.lic2cat2)

    self.lic1cat2 = License()
    self.lic1cat2._id = 1
    self.lic1cat2.name = "lic1cat2"
    self.lic1cat2.files = []
    self.cat2.licenses.append(self.lic1cat2)

    self.lic5cat1 = License()
    self.lic5cat1._id = 5
    self.lic5cat1.name = "a license"
    self.lic5cat1.files = []
    self.cat1.licenses.append(self.lic5cat1)

    # no license found option, for analysis outputs
    self.noLicFound = License()
    self.noLicFound._id = 6
    self.noLicFound.name = "No license found"
    self.noLicFound.files = []
    self.cat4.licenses.append(self.noLicFound)

  def _buildFiles(self, results):
    # should sort alphabetically by path before f1
    self.f2 = File()
    self.f2._id = 2
    self.f2.path = "/first/tmp/f2"
    self.f2.scan_id = 1
    self.f2.findings = {}
    self.lic2cat2.files.append(self.f2)

    self.f1 = File()
    self.f1._id = 1
    self.f1.path = "/tmp/f1"
    self.f1.scan_id = 1
    self.f1.findings = {}
    self.lic2cat2.files.append(self.f1)

    # should sort after f2 and f1 b/c license ID sorts after theirs
    self.f3 = File()
    self.f3._id = 3
    self.f3.path = "/earliest/tmp/f3"
    self.f3.scan_id = 1
    self.f3.findings = {}
    self.lic1cat2.files.append(self.f3)

    self.f4 = File()
    self.f4._id = 4
    self.f4.path = "/tmp/f4"
    self.f4.scan_id = 1
    self.f4.findings = {}
    self.lic1cat2.files.append(self.f4)

    self.f5 = File()
    self.f5._id = 5
    self.f5.path = "/tmp/f5"
    self.f5.scan_id = 1
    self.f5.findings = {}
    self.lic5cat1.files.append(self.f5)

    self.f6 = File()
    self.f6._id = 6
    self.f6.path = "/tmp/f6.png"
    self.f6.scan_id = 1
    self.f6.findings = {
      "extension": "yes",
    }
    self.noLicFound.files.append(self.f6)

    # add some more files for testing findings
    self.f7 = File()
    self.f7._id = 7
    self.f7.path = "/tmp/__init__.py"
    self.f7.scan_id = 1
    self.f7.findings = {
      "emptyfile": "yes",
    }
    self.noLicFound.files.append(self.f7)

    self.f8 = File()
    self.f8._id = 8
    self.f8.path = "/tmp/vendor/dep.py"
    self.f8.scan_id = 1
    self.f8.findings = {
      "thirdparty": "yes",
    }
    self.noLicFound.files.append(self.f8)

    self.f9 = File()
    self.f9._id = 9
    self.f9.path = "/tmp/code.py"
    self.f9.scan_id = 1
    self.f9.findings = {}
    self.noLicFound.files.append(self.f9)

  def _getAnalysisResults(self):
    results = []
    self._buildCategories(results)
    self._buildLicenses(results)
    self._buildFiles(results)
    return results

  ##### Test cases below

  def test_new_reporter_is_in_reset_state(self):
    self.assertIsNone(self.reporter.results)
    self.assertIsNone(self.reporter.rjs)
    self.assertFalse(self.reporter.reportSaved)
    self.assertEqual({}, self.reporter.kwConfig)

  ##### Reporter config function tests

  def test_reporter_can_take_optional_config_params(self):
    configDict = {
      "report-pretty-print": "yes",
    }
    newReporter = JSONReporter(db=self.db, config=configDict)
    self.assertEqual("yes", newReporter.kwConfig["report-pretty-print"])

  def test_can_get_reporter_final_config(self):
    self.db.setConfigValue(key="report-pretty-print", value="yes")
    summary = self.reporter._getFinalConfigValue(key="report-pretty-print")
    self.assertEqual(summary, "yes")

  def test_can_override_db_config_in_reporter_final_config(self):
    self.db.setConfigValue(key="report-pretty-print", value="yes")
    newReporter = JSONReporter(db=self.db, config={"report-pretty-print": "no"})
    summary = newReporter._getFinalConfigValue(key="report-pretty-print")
    self.assertEqual(summary, "no")

  ##### Reporter setup function tests

  def test_can_set_results_and_create_empty_string_for_json(self):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.assertIsInstance(self.reporter.rjs, str)
    self.assertEqual(self.reporter.rjs, "")
    self.assertEqual(self.reporter.results, results)

  ##### Reporter custom JSON encoder tests

  def test_encoder_creates_correct_values(self):
    results = self._getAnalysisResults()
    enc = self.reporter.SLMJSONEncoder()

    # here's a file with findings
    enc_f6 = enc.default(self.f6)
    self.assertEqual(enc_f6["path"], "/tmp/f6.png")
    self.assertEqual(enc_f6["_id"], 6)
    self.assertEqual(enc_f6["findings"], {"extension": "yes"})

    # here's a file with no findings
    enc_f5 = enc.default(self.f5)
    self.assertEqual(enc_f5["path"], "/tmp/f5")
    self.assertEqual(enc_f5["_id"], 5)
    with self.assertRaises(KeyError):
      na = enc_f5["findings"]

    # here's a license
    enc_lic1 = enc.default(self.lic1cat2)
    self.assertEqual(enc_lic1["name"], "lic1cat2")
    self.assertEqual(enc_lic1["_id"], 1)
    self.assertEqual(enc_lic1["numFiles"], 2)
    self.assertEqual(enc_lic1["files"], self.lic1cat2.files)

    # here's a category
    enc_cat2 = enc.default(self.cat2)
    self.assertEqual(enc_cat2["name"], "catID2")
    self.assertEqual(enc_cat2["_id"], 2)
    self.assertEqual(enc_cat2["numFiles"], 4)
    self.assertEqual(enc_cat2["licenses"], self.cat2.licenses)

  ##### Reporter helpers

  def test_helper_can_get_number_of_files_for_license(self):
    results = self._getAnalysisResults()
    enc = self.reporter.SLMJSONEncoder()
    numFiles = enc._getNumFilesForLicense(self.lic1cat2)
    self.assertEqual(numFiles, 2)

  def test_helper_can_get_number_of_files_for_category(self):
    results = self._getAnalysisResults()
    enc = self.reporter.SLMJSONEncoder()
    numFiles = enc._getNumFilesForCategory(self.cat2)
    self.assertEqual(numFiles, 4)

  ##### Reporter generate function tests

  def test_save_report_fails_if_results_not_ready(self):
    with self.assertRaises(ReportNotReadyError):
      self.reporter.save(path="/tmp/fake/whatever.json")
    self.assertFalse(self.reporter.reportSaved)

  @mock.patch('slm.reports.json.open')
  @mock.patch('slm.reports.json.json.dump')
  def test_save_calls_functions_to_save(self, dump_mock, open_mock):
    outfile = "/tmp/newfile.json"
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    self.reporter.save(path=outfile)

    dump_mock.assert_called()
    args = dump_mock.call_args
    self.assertEqual(args[0][0], results)
    self.assertEqual(args[1], {"cls": JSONReporter.SLMJSONEncoder})
    open_mock.assert_called_with(outfile, "w")

  ##### Reporter save function tests

  @mock.patch('slm.reports.json.open')
  @mock.patch('slm.reports.json.os.path.exists', return_value=True)
  def test_save_check_raises_exception_if_file_already_exists(self, os_exists, open_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)

    with self.assertRaises(ReportFileError):
      self.reporter._saveCheck(path="/tmp/fake/existing.json")

  @mock.patch('slm.reports.json.open')
  @mock.patch('slm.reports.json.os.path.exists', return_value=True)
  @mock.patch('slm.reports.json.os.access', return_value=True)
  def test_save_check_doesnt_raise_exception_if_replace_flag_set(self, os_access, os_exists, open_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)

    try:
      self.reporter._saveCheck(path="/tmp/fake/existing.json", replace=True)
    except ReportFileError:
      self.fail("ReportFileError raised even though replace flag is True")

  @mock.patch('slm.reports.json.open')
  @mock.patch('slm.reports.json.os.access', return_value=False)
  def test_save_check_fails_if_no_write_permission_for_path(self, os_access, open_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)

    with self.assertRaises(ReportFileError):
      self.reporter._saveCheck(path="/tmp/readonly/report.json")

  def test_save_check_fails_if_report_not_ready_yet(self):
    with self.assertRaises(ReportNotReadyError):
      self.reporter._saveCheck(path="whatever")

  @mock.patch('slm.reports.json.open')
  @mock.patch('slm.reports.json.JSONReporter._saveCheck')
  def test_save_calls_save_checker(self, check_mock, open_mock):
    results = self._getAnalysisResults()
    self.reporter.setResults(results)
    path = "something"
    replace = True

    self.reporter.save(path=path, replace=replace)

    check_mock.assert_called_with(path=path, replace=replace)
    open_mock.assert_called_with(path, "w")
