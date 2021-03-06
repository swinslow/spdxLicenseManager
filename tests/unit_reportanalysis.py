# tests/unit_reportanalysis.py
#
# Unit test for spdxLicenseManager: analyzing licenses and files for reports.
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
from collections import OrderedDict

from slm.datatypes import Category, File, License, Scan, Subproject
from slm.projectdb import ProjectDB, ProjectDBQueryError
from slm.reports.common import ReportAnalysisError
from slm.reports.analysis import Analyzer

class ReportAnalysisTestSuite(unittest.TestCase):
  """spdxLicenseManager analysis for reporting unit test suite."""

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

    # create analyzer
    self.analyzer = Analyzer(db=self.db)

  def tearDown(self):
    pass

  def insertSampleCategoryData(self):
    categories = [
      Category(_id=1, name="a category", order=3),
      Category(_id=2, name="cat", order=2),
      Category(_id=3, name="blah category", order=1),
      Category(_id=4, name="no lic category", order=4),
    ]
    self.db.session.bulk_save_objects(categories)
    self.db.session.commit()

  def insertSampleLicenseData(self):
    licenses = [
      License(_id=1, name="DoAnything", category_id=1),
      License(_id=2, name="HarshEULA", category_id=2),
      License(_id=3, name="293PageEULA", category_id=3),
      License(_id=4, name="DoAnythingNoncommercial", category_id=1),
      License(_id=5, name="No license found", category_id=4),
      License(_id=6, name="Also no license found", category_id=4),
      License(_id=7, name="LicWithNoFiles", category_id=4),
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
      Scan(_id=2, subproject_id=1, scan_dt=datetime.date(2017, 2, 10),
        desc="monthly scan 2"),
      Scan(_id=3, subproject_id=1, scan_dt=datetime.date(2017, 3, 10),
        desc="monthly scan 3"),
    ]
    self.db.session.bulk_save_objects(scans)
    self.db.session.commit()

  def insertSampleFileData(self):
    self.f1 = File(_id=1, scan_id=1, license_id=1, path="/tmp/f1", sha1=None, md5="abcdef", sha256=None)
    self.f2 = File(_id=2, scan_id=1, license_id=4, path="/tmp/f2", sha1=None, md5=None, sha256="abcdef")
    self.f3 = File(_id=3, scan_id=1, license_id=2, path="/tmp/f3", sha1="abcdef", md5=None, sha256=None)
    self.f4 = File(_id=4, scan_id=1, license_id=2, path="/tmp/f4", sha1=None, md5=None, sha256=None)
    self.f5 = File(_id=5, scan_id=1, license_id=5, path="/tmp/nolic/image.png", sha1=None, md5=None, sha256=None)
    self.f6 = File(_id=6, scan_id=1, license_id=2, path="/tmp/nolic/vendor/whatever", sha1=None, md5=None, sha256=None)
    self.f7 = File(_id=7, scan_id=1, license_id=6, path="/tmp/nolic/vendor/image-both.png", sha1=None, md5=None, sha256=None)
    self.f8 = File(_id=8, scan_id=1, license_id=6, path="/tmp/nolic/emptyfile", sha1=None, md5="d41d8cd98f00b204e9800998ecf8427e", sha256=None)
    self.f9 = File(_id=9, scan_id=1, license_id=6, path="/tmp/nolic/vendor/emptyfile", sha1=None, md5="d41d8cd98f00b204e9800998ecf8427e", sha256=None)
    self.f10 = File(_id=10, scan_id=1, license_id=6, path="/tmp/nolic/emptyfile.png", sha1=None, md5="d41d8cd98f00b204e9800998ecf8427e", sha256=None)
    self.f11 = File(_id=11, scan_id=1, license_id=6, path="/tmp/nolic/vendor/emptyfile.json", sha1=None, md5="d41d8cd98f00b204e9800998ecf8427e", sha256=None)
    self.f21 = File(_id=21, scan_id=2, license_id=1, path="/scan2/tmp/f1", sha1=None, md5="abcdef", sha256=None)
    self.f22 = File(_id=22, scan_id=2, license_id=4, path="/scan2/tmp/f2", sha1=None, md5=None, sha256="abcdef")
    self.f23 = File(_id=23, scan_id=2, license_id=3, path="/scan2/tmp/f3-lic3", sha1="abcdef", md5=None, sha256=None)
    self.f24 = File(_id=24, scan_id=2, license_id=2, path="/scan2/tmp/f4", sha1=None, md5=None, sha256=None)
    self.f31 = File(_id=31, scan_id=3, license_id=1, path="/scan3/tmp/f1", sha1=None, md5="abcdef", sha256=None)
    self.f32 = File(_id=32, scan_id=3, license_id=4, path="/scan3/tmp/f2", sha1=None, md5=None, sha256="abcdef")
    self.f33 = File(_id=33, scan_id=3, license_id=2, path="/scan3/tmp/f3", sha1="abcdef", md5=None, sha256=None)
    self.f34 = File(_id=34, scan_id=3, license_id=2, path="/scan3/tmp/f4", sha1=None, md5=None, sha256=None)
    self.files = [
      self.f1, self.f2, self.f3, self.f4, self.f5,
      self.f6, self.f7, self.f8, self.f9, self.f10, self.f11,
      self.f21, self.f22, self.f23, self.f24,
      self.f31, self.f32, self.f33, self.f34,
    ]
    self.db.session.bulk_save_objects(self.files)
    self.db.session.commit()

  ##### Helpers for tests

  def _checkFileExtFindingIsNone(self, file_id):
    ext = self.analyzer._getFile(file_id).findings.get("extension", None)
    self.assertIsNone(ext)

  def _checkFileExtFindingIsYes(self, file_id):
    ext = self.analyzer._getFile(file_id).findings.get("extension", None)
    self.assertEqual("yes", ext)

  def _checkFileEmptyFindingIsNone(self, file_id):
    empty = self.analyzer._getFile(file_id).findings.get("emptyfile", None)
    self.assertIsNone(empty)

  def _checkFileEmptyFindingIsYes(self, file_id):
    empty = self.analyzer._getFile(file_id).findings.get("emptyfile", None)
    self.assertEqual("yes", empty)

  def _checkFileDirFindingIsNone(self, file_id):
    tp = self.analyzer._getFile(file_id).findings.get("thirdparty", None)
    self.assertIsNone(tp)

  def _checkFileDirFindingIsYes(self, file_id):
    tp = self.analyzer._getFile(file_id).findings.get("thirdparty", None)
    self.assertEqual("yes", tp)

  ##### Test cases below

  def test_analyzer_is_in_reset_state(self):
    self.assertEqual(self.db, self.analyzer.db)
    self.assertFalse(self.analyzer.isReady)
    self.assertIsNone(self.analyzer.primaryScan)
    self.assertEqual(OrderedDict(), self.analyzer.primaryScanCategories)
    self.assertEqual({}, self.analyzer.kwConfig)
    self.assertFalse(self.analyzer.analysisDone)

  def test_analyzer_retrieves_all_categories_for_report(self):
    self.analyzer._buildScanCategories()
    self.assertEqual(len(self.analyzer.primaryScanCategories), 4)

  def test_analyzer_still_not_ready_after_just_buildScanCategories(self):
    self.analyzer._buildScanCategories()
    self.assertFalse(self.analyzer.isReady)

  def test_analyzer_cannot_call_buildScanCategories_twice(self):
    self.analyzer._buildScanCategories()
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._buildScanCategories()

  def test_analyzer_builds_categories_with_OD_for_licenses(self):
    self.analyzer._buildScanCategories()
    for cat in self.analyzer.primaryScanCategories.values():
      self.assertIs(type(cat.licensesSorted), OrderedDict)
    c1 = self.analyzer.primaryScanCategories[1]
    l1 = c1.licensesSorted[1]
    self.assertEqual(l1._id, 1)
    self.assertEqual(l1.name, "DoAnything")
    l4 = c1.licensesSorted[4]
    self.assertEqual(l4._id, 4)
    self.assertEqual(l4.name, "DoAnythingNoncommercial")
    # and it doesn't have licenses from a different category
    with self.assertRaises(KeyError):
      c1.licensesSorted[2]

  def test_analyzer_builds_categories_OD_in_sort_order(self):
    self.analyzer._buildScanCategories()
    (c_id1, c1) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual(3, c_id1)
    self.assertEqual("blah category", c1.name)
    (c_id2, c2) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual(2, c_id2)
    self.assertEqual("cat", c2.name)
    (c_id3, c3) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual(1, c_id3)
    self.assertEqual("a category", c3.name)

  ##### Analyzer adding files tests

  def test_analyzer_cannot_add_files_before_categories_are_built(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._addFiles(scan_id=1)

  def test_analyzer_cannot_add_files_from_invalid_scan_id(self):
    self.analyzer._buildScanCategories()
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._addFiles(scan_id=187)

  def test_analyzer_can_add_files_to_categories_for_a_scan(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)

    # check category 1, with one license and NO FILES
    (c_id1, c1) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("blah category", c1.name)
    (l_id11, l11) = c1.licensesSorted.popitem(last=False)
    self.assertEqual("293PageEULA", l11.name)
    self.assertEqual([], list(l11.filesSorted.items()))

    # check category 2, with one license and three files
    (c_id2, c2) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("cat", c2.name)
    (l_id21, l21) = c2.licensesSorted.popitem(last=False)
    self.assertEqual("HarshEULA", l21.name)
    self.assertEqual(len(l21.filesSorted), 3)
    (f_id211, f211) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id211, 3)
    self.assertEqual(f211.path, "/tmp/f3")
    self.assertEqual(f211.findings, {})
    (f_id212, f212) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id212, 4)
    self.assertEqual(f212.path, "/tmp/f4")
    self.assertEqual(f212.findings, {})
    (f_id216, f216) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id216, 6)
    self.assertEqual(f216.path, "/tmp/nolic/vendor/whatever")
    self.assertEqual(f216.findings, {}) # haven't run analysis yet

    # check category 3, with two licenses and two files
    (c_id3, c3) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("a category", c3.name)
    (l_id31, l31) = c3.licensesSorted.popitem(last=False)
    self.assertEqual("DoAnything", l31.name)
    self.assertEqual(len(l31.filesSorted), 1)
    (f_id311, f311) = l31.filesSorted.popitem(last=False)
    self.assertEqual(f_id311, 1)
    self.assertEqual(f311.path, "/tmp/f1")
    self.assertEqual(f311.findings, {})
    (l_id32, l32) = c3.licensesSorted.popitem(last=False)
    self.assertEqual("DoAnythingNoncommercial", l32.name)
    self.assertEqual(len(l32.filesSorted), 1)
    (f_id321, f321) = l32.filesSorted.popitem(last=False)
    self.assertEqual(f_id321, 2)
    self.assertEqual(f321.path, "/tmp/f2")
    self.assertEqual(f321.findings, {})

  def test_can_add_files_from_multiple_scans(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._addFiles(scan_id=3)

  # check category 1, with one license and still NO FILES
    (c_id1, c1) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("blah category", c1.name)
    (l_id11, l11) = c1.licensesSorted.popitem(last=False)
    self.assertEqual("293PageEULA", l11.name)
    self.assertEqual([], list(l11.filesSorted.items()))

  # check category 2, with one license and now five files
    (c_id2, c2) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("cat", c2.name)
    (l_id21, l21) = c2.licensesSorted.popitem(last=False)
    self.assertEqual("HarshEULA", l21.name)
    self.assertEqual(len(l21.filesSorted), 5)
    (f_id211, f211) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id211, 3)
    self.assertEqual(f211.path, "/tmp/f3")
    self.assertEqual(f211.findings, {})
    (f_id212, f212) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id212, 4)
    self.assertEqual(f212.path, "/tmp/f4")
    self.assertEqual(f212.findings, {})
    (f_id216, f216) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id216, 6)
    self.assertEqual(f216.path, "/tmp/nolic/vendor/whatever")
    self.assertEqual(f216.findings, {}) # haven't run analysis yet
    (f3_id211, f3211) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f3_id211, 33)
    self.assertEqual(f3211.path, "/scan3/tmp/f3")
    self.assertEqual(f3211.findings, {})
    (f3_id212, f3212) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f3_id212, 34)
    self.assertEqual(f3212.path, "/scan3/tmp/f4")
    self.assertEqual(f3212.findings, {})

  def test_analyzer_marks_cats_and_lics_that_have_files(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)

    # check categories
    c1 = self.analyzer._getCategory(category_id=1)
    self.assertTrue(c1.hasFiles)
    c2 = self.analyzer._getCategory(category_id=2)
    self.assertTrue(c2.hasFiles)
    c3 = self.analyzer._getCategory(category_id=3)
    self.assertFalse(c3.hasFiles)

    # check licenses
    l2 = self.analyzer._getLicense(license_id=2)
    self.assertTrue(l2.hasFiles)
    l4 = self.analyzer._getLicense(license_id=4)
    self.assertTrue(l4.hasFiles)
    l7 = self.analyzer._getLicense(license_id=7)
    self.assertFalse(l7.hasFiles)

  ##### Analyzer config params tests

  def test_analyzer_can_take_optional_config_params(self):
    configDict = {
      "analyze-extensions": "yes",
      "analyze-extensions-list": "json;jpeg;png"
    }
    newAnalyzer = Analyzer(db=self.db, config=configDict)
    self.assertEqual("yes", newAnalyzer.kwConfig["analyze-extensions"])
    self.assertEqual("json;jpeg;png",
      newAnalyzer.kwConfig["analyze-extensions-list"])

  def test_can_get_analyze_final_config_from_analyzer(self):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    exts = self.analyzer._getFinalConfigValue(key="analyze-extensions")
    self.assertEqual(exts, "yes")

  def test_can_override_db_config_in_analyzer_final_config(self):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    newAnalyzer = Analyzer(db=self.db, config={"analyze-extensions": "no"})
    exts = newAnalyzer._getFinalConfigValue(key="analyze-extensions")
    self.assertEqual(exts, "no")

  ##### Analyzer main analysis function tests

  def test_analyzer_cannot_analyze_before_categories_are_built(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._runAnalysis()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExtensions')
  def test_analyzer_runs_extensions_check_if_set(self, ext_mock):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    ext_mock.assert_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExtensions')
  def test_analyzer_does_not_run_extensions_check_if_not_set(self, ext_mock):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    ext_mock.assert_not_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExtensions')
  def test_analyzer_does_not_run_extensions_check_if_set_to_no(self, ext_mock):
    self.db.setConfigValue(key="analyze-extensions", value="no")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    ext_mock.assert_not_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeThirdparty')
  def test_analyzer_runs_thirparty_check_if_set(self, tp_mock):
    self.db.setConfigValue(key="analyze-thirdparty", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    tp_mock.assert_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeThirdparty')
  def test_analyzer_does_not_run_thirdparty_check_if_not_set(self, tp_mock):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    tp_mock.assert_not_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeEmptyFile')
  def test_analyzer_runs_emptyfile_check_if_set(self, empty_mock):
    self.db.setConfigValue(key="analyze-emptyfile", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    empty_mock.assert_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeEmptyFile')
  def test_analyzer_does_not_run_emptyfile_check_if_not_set(self, empty_mock):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    empty_mock.assert_not_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExcludePathPrefix')
  def test_analyzer_runs_excludePathPrefix_if_set(self, path_mock):
    self.db.setConfigValue(key="analyze-exclude-path-prefix", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    path_mock.assert_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExcludePathPrefix')
  def test_analyzer_does_not_run_excludePathPrefix_if_not_set(self, path_mock):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    path_mock.assert_not_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExcludeEmptyCatsAndLics')
  def test_analyzer_runs_excludeEmptyCatsAndLics_if_set(self, ecl_mock):
    self.db.setConfigValue(key="analyze-exclude-empty-cats-and-lics", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    ecl_mock.assert_called()

  @mock.patch('slm.reports.analysis.Analyzer._analyzeExcludeEmptyCatsAndLics')
  def test_analyzer_does_not_run_excludeEmptyCatsAndLics_if_not_set(self, ecl_mock):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    ecl_mock.assert_not_called()

  ##### getter helper tests

  def test_analyzer_cannot_get_specific_cat_before_building_categories(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getCategory(category_id=3)

  def test_analyzer_returns_none_if_getting_specific_cat_by_unknown_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    cat = self.analyzer._getCategory(category_id=77)
    self.assertIsNone(cat)

  def test_analyzer_can_get_specific_category_by_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    cat = self.analyzer._getCategory(category_id=3)
    self.assertEqual("blah category", cat.name)

  def test_analyzer_cannot_get_specific_lic_before_building_categories(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getLicense(license_id=6)

  def test_analyzer_returns_none_if_getting_specific_lic_by_unknown_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    lic = self.analyzer._getLicense(license_id=77)
    self.assertIsNone(lic)

  def test_analyzer_can_get_specific_license_by_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    lic = self.analyzer._getLicense(license_id=6)
    self.assertEqual("Also no license found", lic.name)

  def test_analyzer_cannot_get_specific_file_before_building_categories(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getFile(7)

  def test_analyzer_returns_none_if_getting_specific_file_by_unknown_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    f = self.analyzer._getFile(77)
    self.assertIsNone(f)

  def test_analyzer_can_get_specific_file_by_id(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()
    f = self.analyzer._getFile(file_id=7)
    self.assertEqual("/tmp/nolic/vendor/image-both.png", f.path)

  ##### file extension analysis tests

  def test_can_parse_file_extension_string(self):
    extString = "json;jpeg;png;gif"
    self.db.setConfigValue(key="analyze-extensions-list", value=extString)
    exts = self.analyzer._parseExtConfig()
    # extensions are sorted in alphabetical order
    self.assertEqual(["gif","jpeg","json","png"], exts)

  def test_extension_string_parser_returns_empty_list_if_not_set(self):
    exts = self.analyzer._parseExtConfig()
    self.assertEqual([], exts)

  def test_ignore_whitespace_in_file_extension_string(self):
    extString = "   json ;  jpeg;   png  ;gif     "
    self.db.setConfigValue(key="analyze-extensions-list", value=extString)
    exts = self.analyzer._parseExtConfig()
    # extensions are sorted in alphabetical order
    self.assertEqual(["gif","jpeg","json","png"], exts)

  def test_files_with_extension_match_get_extra_flag_and_others_dont(self):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    extString = "json;jpeg;png;gif"
    self.db.setConfigValue(key="analyze-extensions-list", value=extString)
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()

    # check specific files
    self._checkFileExtFindingIsNone(1)
    self._checkFileExtFindingIsNone(2)
    self._checkFileExtFindingIsNone(3)
    self._checkFileExtFindingIsNone(4)
    self._checkFileExtFindingIsYes(5)
    self._checkFileExtFindingIsNone(6)
    self._checkFileExtFindingIsYes(7)
    self._checkFileExtFindingIsNone(8)
    self._checkFileExtFindingIsNone(9)
    self._checkFileExtFindingIsYes(10)
    self._checkFileExtFindingIsYes(11)

  ##### empty file analysis tests

  def test_empty_files_get_extra_flag_and_others_dont(self):
    self.db.setConfigValue(key="analyze-emptyfile", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()

    # check specific files
    self._checkFileEmptyFindingIsNone(1)
    self._checkFileEmptyFindingIsNone(2)
    self._checkFileEmptyFindingIsNone(3)
    self._checkFileEmptyFindingIsNone(4)
    self._checkFileEmptyFindingIsNone(5)
    self._checkFileEmptyFindingIsNone(6)
    self._checkFileEmptyFindingIsNone(7)
    self._checkFileEmptyFindingIsYes(8)
    self._checkFileEmptyFindingIsYes(9)
    self._checkFileEmptyFindingIsYes(10)
    self._checkFileEmptyFindingIsYes(11)

  ##### third party directory analysis tests

  def test_can_parse_thirdparty_dirs_string(self):
    dirString = "vendor;thirdparty;third-party"
    self.db.setConfigValue(key="analyze-thirdparty-dirs", value=dirString)
    dirs = self.analyzer._parseDirConfig()
    # directories are sorted in alphabetical order
    self.assertEqual(["third-party","thirdparty","vendor"], dirs)

  def test_directories_string_parser_returns_empty_list_if_not_set(self):
    dirs = self.analyzer._parseDirConfig()
    self.assertEqual([], dirs)

  def test_ignore_whitespace_in_thirdparty_dirs_string(self):
    dirString = "   thirdparty ;  vendor  ;third-party     "
    self.db.setConfigValue(key="analyze-thirdparty-dirs", value=dirString)
    dirs = self.analyzer._parseDirConfig()
    # directories are sorted in alphabetical order
    self.assertEqual(["third-party","thirdparty","vendor"], dirs)

  def test_files_with_directory_match_get_extra_flag_and_others_dont(self):
    self.db.setConfigValue(key="analyze-thirdparty", value="yes")
    dirString = "vendor;thirdparty;third-party"
    self.db.setConfigValue(key="analyze-thirdparty-dirs", value=dirString)
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()

    # check specific files
    self._checkFileDirFindingIsNone(1)
    self._checkFileDirFindingIsNone(2)
    self._checkFileDirFindingIsNone(3)
    self._checkFileDirFindingIsNone(4)
    self._checkFileDirFindingIsNone(5)
    self._checkFileDirFindingIsYes(6)
    self._checkFileDirFindingIsYes(7)
    self._checkFileDirFindingIsNone(8)
    self._checkFileDirFindingIsYes(9)
    self._checkFileDirFindingIsNone(10)
    self._checkFileDirFindingIsYes(11)

  ##### exclude path prefix analysis tests

  def test_analyzer_can_exclude_common_path_prefix(self):
    self.db.setConfigValue(key="analyze-exclude-path-prefix", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()

    # check that file paths have changed
    for cat in self.analyzer.primaryScanCategories.values():
      for lic in cat.licensesSorted.values():
        for file in lic.filesSorted.values():
          self.assertNotIn("tmp", file.path)

  ##### exclude empty categories and licenses analysis tests

  def test_analyzer_can_exclude_empty_cats_and_lics(self):
    self.db.setConfigValue(key="analyze-exclude-empty-cats-and-lics", value="yes")
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)
    self.analyzer._runAnalysis()

    # check that empty cats are gone
    with self.assertRaises(KeyError):
      na = self.analyzer.primaryScanCategories[3]
    # and check that empty licenses are gone
    cat4 = self.analyzer.primaryScanCategories[4]
    with self.assertRaises(KeyError):
      na = cat4.licensesSorted[7]

    # and check that cats and licenses with files are still present
    self.assertEqual(cat4.name, "no lic category")
    self.assertEqual(cat4.licensesSorted[6].name, "Also no license found")

  ##### main analysis function tests

  def test_can_analyze_and_get_results(self):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    results = self.analyzer.runAnalysis(scan_id=1)
    self.assertEqual(OrderedDict, type(results))
    self.assertEqual(4, len(results.items()))
    cat1 = results[1]
    self.assertEqual("a category", cat1.name)
    self.assertTrue(self.analyzer.analysisDone)

  def test_can_analyze_and_get_results_for_multiple_scans(self):
    self.db.setConfigValue(key="analyze-extensions", value="yes")
    results = self.analyzer.runAnalysis(scan_ids=[1,3])
    self.assertEqual(OrderedDict, type(results))
    self.assertEqual(4, len(results.items()))
    cat1 = results[1]
    self.assertEqual("a category", cat1.name)
    self.assertTrue(self.analyzer.analysisDone)

  def test_cannot_analyze_invalid_scan_id(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.runAnalysis(scan_id=187)

  def test_cannot_analyze_invalid_scan_id_in_multiple_ids(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.runAnalysis(scan_ids=[1,3,187])

  def test_cannot_analyze_with_singular_and_multiple_scan_ids(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.runAnalysis(scan_id=1, scan_ids=[1,3])

  ##### create list results from OrderedDict results

  def test_cannot_get_list_results_before_results_are_generated(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.getResultsAsList()

    self.analyzer._buildScanCategories()
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.getResultsAsList()

    self.analyzer._addFiles(scan_id=1)
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.getResultsAsList()

  def test_can_get_list_results_from_OrderedDict_results(self):
    self.db.setConfigValue(key="analyze-exclude-empty-cats-and-lics", value="yes")
    self.analyzer.runAnalysis(scan_id=1)

    list_results = self.analyzer.getResultsAsList()

    # check top-level list of categories
    # should be sorted by order and should exclude empty categories
    self.assertIsInstance(list_results, list)
    self.assertEqual(len(list_results), 3)
    cat2 = list_results[0]
    self.assertIsInstance(cat2, Category)
    self.assertEqual(cat2.name, "cat")
    self.assertEqual(cat2._id, 2)

    # check licenses within a category
    # should be sorted alphabetically and should exclude empty licenses
    cat4 = list_results[2]
    self.assertIsInstance(cat4.licenses, list)
    self.assertEqual(len(cat4.licenses), 2)
    lic6 = cat4.licenses[0]
    self.assertIsInstance(lic6, License)
    self.assertEqual(lic6.name, "Also no license found")
    self.assertEqual(lic6._id, 6)

    # check files within a license
    self.assertIsInstance(lic6.files, list)
    self.assertEqual(len(lic6.files), 5)
    self.assertIsInstance(lic6.files[0], File)

  ##### Split string into separate scan IDs

  def test_can_split_string_with_individual_scan_ids(self):
    sstring = "1,3,10,6,2"
    scan_ids = self.analyzer.splitScanIDString(sstring)
    # scan IDs should be included regardless of whether they're actual
    # scans, and should be sorted
    self.assertEqual(scan_ids, [1,2,3,6,10])

  def test_can_split_string_with_range_of_scan_ids(self):
    sstring = "1,8,4-6,9"
    scan_ids = self.analyzer.splitScanIDString(sstring)
    self.assertEqual(scan_ids, [1,4,5,6,8,9])

  def test_raises_error_if_invalid_text_found(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("oops")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("1,oops")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("oops,3")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("1,oops,3")

  def test_ids_not_duplicated_if_included_repeatedly(self):
    sstring = "1,1-4,1,4,7-8,7-8,7"
    scan_ids = self.analyzer.splitScanIDString(sstring)
    self.assertEqual(scan_ids, [1,2,3,4,7,8])

  def test_raises_error_if_range_is_backwards(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("9-2")

  def test_raises_error_if_range_format_is_invalid(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("9-")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("9-10-15")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("-9")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("-")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("9--12")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer.splitScanIDString("-9-10")

  def test_helper_returns_int_from_string(self):
    i = self.analyzer._getIntFromStringScanID("3")
    self.assertEqual(i, 3)

  def test_helper_raises_report_analysis_error_for_non_integers(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID("")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID("a")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID("3-")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID("3a")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID(",")
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._getIntFromStringScanID("3:")
