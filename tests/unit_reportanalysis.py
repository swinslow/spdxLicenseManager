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

  def test_analyzer_is_in_reset_state(self):
    self.assertEqual(self.db, self.analyzer.db)
    self.assertFalse(self.analyzer.isReady)
    self.assertIsNone(self.analyzer.primaryScan)
    self.assertEqual(OrderedDict(), self.analyzer.primaryScanCategories)
    self.assertEqual({}, self.analyzer.kwConfig)

  def test_analyzer_retrieves_all_categories_for_report(self):
    self.analyzer._buildScanCategories()
    self.assertEqual(len(self.analyzer.primaryScanCategories), 3)

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

  def test_analyzer_cannot_add_files_before_categories_are_built(self):
    with self.assertRaises(ReportAnalysisError):
      self.analyzer._addFiles(scan_id=1)

  def test_analyzer_can_add_files_to_categories_for_a_scan(self):
    self.analyzer._buildScanCategories()
    self.analyzer._addFiles(scan_id=1)

    # check category 1, with one license and NO FILES
    (c_id1, c1) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("blah category", c1.name)
    (l_id11, l11) = c1.licensesSorted.popitem(last=False)
    self.assertEqual("293PageEULA", l11.name)
    self.assertEqual([], list(l11.filesSorted.items()))

    # check category 2, with one license and two files
    (c_id2, c2) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("cat", c2.name)
    (l_id21, l21) = c2.licensesSorted.popitem(last=False)
    self.assertEqual("HarshEULA", l21.name)
    (f_id211, f211) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id211, 3)
    self.assertEqual(f211.path, "/tmp/f3")
    (f_id212, f212) = l21.filesSorted.popitem(last=False)
    self.assertEqual(f_id212, 4)
    self.assertEqual(f212.path, "/tmp/f4")

    # check category 3, with two licenses and two files
    (c_id3, c3) = self.analyzer.primaryScanCategories.popitem(last=False)
    self.assertEqual("a category", c3.name)
    (l_id31, l31) = c3.licensesSorted.popitem(last=False)
    self.assertEqual("DoAnything", l31.name)
    (f_id311, f311) = l31.filesSorted.popitem(last=False)
    self.assertEqual(f_id311, 1)
    self.assertEqual(f311.path, "/tmp/f1")
    (l_id32, l32) = c3.licensesSorted.popitem(last=False)
    self.assertEqual("DoAnythingNoncommercial", l32.name)
    (f_id321, f321) = l32.filesSorted.popitem(last=False)
    self.assertEqual(f_id321, 2)
    self.assertEqual(f321.path, "/tmp/f2")

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
