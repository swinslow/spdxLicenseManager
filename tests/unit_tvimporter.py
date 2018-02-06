# tests/unit_tvimporter.py
#
# Unit test for spdxLicenseManager: SPDX tag-value importer.
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

import datetime
import unittest
from unittest import mock

from slm.tvImporter import TVImporter
from slm.tvParser import ParsedFileData
from slm.datatypes import Category, Conversion, License, Scan, Subproject
from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError, ProjectDBDeleteError)

def createFD(path, license, md5=None, sha1=None, sha256=None):
  """Helper to create sample file data entries for testing."""
  fd = ParsedFileData()
  fd.path = path
  fd.license = license
  fd.md5 = md5
  fd.sha1 = sha1
  fd.sha256 = sha256
  return fd

class TVImporterTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX tag-value importer unit test suite."""

  def setUp(self):
    # create importer object
    self.importer = TVImporter()

    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleCategoryData()
    self.insertSampleLicenseData()
    self.insertSampleConversionData()
    self.insertSampleSubprojectData()
    self.insertSampleScanData()

    # build sample file data list
    self.fd1 = createFD("/tmp/f1", "DoAnything", md5="abcdef")
    self.fd2 = createFD("/tmp/f2", "DoAnythingNoncommercial", sha256="abcdef")
    self.fd3 = createFD("/tmp/f3", "HarshEULA", sha1="abcdef")
    self.fd4 = createFD("/tmp/f4", "HarshEULA")
    self.fdList = [self.fd1, self.fd2, self.fd3, self.fd4]
    # not in fdList by default
    self.fd5 = createFD("/tmp/badLicense", "UnknownLicense")
    self.fd6 = createFD("/tmp/badLic2", "SecondUnknownLic")
    self.fdConvert = createFD("/tmp/needsConvert", "293")

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

  def insertSampleConversionData(self):
    conversions = [
      Conversion(_id=1, old_text="293", new_license_id=3),
      Conversion(_id=2, old_text="NC", new_license_id=4),
      Conversion(_id=3, old_text="anything", new_license_id=1),
      Conversion(_id=4, old_text="Anything", new_license_id=1),
    ]
    self.db.session.bulk_save_objects(conversions)
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

  ##### Test cases below

  def test_new_importer_is_in_expected_reset_state(self):
    self.assertEqual(self.importer.scanChecked, False)
    self.assertEqual(self.importer.licensesAll, [])
    self.assertEqual(self.importer.licensesUnknown, [])
    self.assertEqual(self.importer.licensesMapping, {})
    self.assertEqual(self.importer.pathDuplicates, [])
    self.assertEqual(self.importer.importedCount, 0)

  def test_import_fails_if_scan_not_checked_first(self):
    with self.assertRaises(ProjectDBInsertError):
      self.importer.importFileDataList(fdList=self.fdList, db=self.db,
        scan_id=self.scan_id)

  def test_cannot_check_without_providing_valid_fdList(self):
    with self.assertRaises(ProjectDBInsertError):
      self.importer.checkFileDataList(db=self.db)

  def test_cannot_check_without_providing_database(self):
    with self.assertRaises(ProjectDBInsertError):
      self.importer.checkFileDataList(fdList=self.fdList)

  def test_checking_valid_fdList_returns_true(self):
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertEqual(True, retval)

  def test_checker_returns_false_if_any_licenses_are_unknown(self):
    self.fdList.append(self.fd5)
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertEqual(False, retval)

  def test_can_get_license_list_if_any_are_unknown(self):
    self.fdList.append(self.fd5)
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    unknowns = self.importer.getUnknowns()
    self.assertIn("UnknownLicense", unknowns)
    self.assertNotIn("DoAnything", unknowns)
    self.assertNotIn("HarshEULA", unknowns)

  def test_license_list_is_sorted_if_multiple_are_unknown(self):
    self.fdList.append(self.fd5)
    self.fdList.append(self.fd6)
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    unknowns = self.importer.getUnknowns()
    self.assertEqual("SecondUnknownLic", unknowns[0])
    self.assertEqual("UnknownLicense", unknowns[1])

  def test_checker_returns_true_if_all_paths_are_unique(self):
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertEqual(True, retval)

  def test_checker_returns_false_if_any_paths_are_duplicates(self):
    fdup = createFD("/tmp/f2", "DoAnythingNoncommercial", sha256="abcdef")
    self.fdList.append(fdup)
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertEqual(False, retval)

  def test_duplicates_list_is_empty_if_all_paths_are_unique(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    dups = self.importer.getDuplicatePaths()
    self.assertEqual([], dups)

  def test_duplicates_list_has_paths_if_any_paths_are_duplicates(self):
    fdup = createFD("/tmp/f2", "DoAnythingNoncommercial", sha256="abcdef")
    self.fdList.append(fdup)
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    dups = self.importer.getDuplicatePaths()
    self.assertEqual(["/tmp/f2"], dups)

  def test_can_get_duplicate_paths_after_checker_if_any(self):
    fdup = createFD("/tmp/f2", "DoAnythingNoncommercial", sha256="abcdef")
    self.fdList.append(fdup)
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    dups = self.importer.getDuplicatePaths()
    self.assertIn("/tmp/f2", dups)
    self.assertNotIn("/tmp/f1", dups)

  def test_checker_returns_true_if_all_is_good(self):
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertEqual(True, retval)

  def test_reads_licenses_into_licensesAll(self):
    # fill in finalLicense, since we are skipping _applyConversions
    for fd in self.fdList:
      fd.finalLicense = fd.license
    self.importer._checkFileDataListForLicenses(fdList=self.fdList, db=self.db)
    self.assertIn("DoAnything", self.importer.licensesAll)

  def test_reads_only_unknown_licenses_into_licensesUnknown(self):
    self.fdList.append(self.fd5)
    # fill in finalLicense, since we are skipping _applyConversions
    for fd in self.fdList:
      fd.finalLicense = fd.license
    self.importer._checkFileDataListForLicenses(fdList=self.fdList, db=self.db)
    self.assertIn("UnknownLicense", self.importer.licensesUnknown)
    self.assertNotIn("DoAnything", self.importer.licensesUnknown)

  def test_reads_only_known_licenses_into_licensesMapping(self):
    self.fdList.append(self.fd5)
    # fill in finalLicense, since we are skipping _applyConversions
    for fd in self.fdList:
      fd.finalLicense = fd.license
    self.importer._checkFileDataListForLicenses(fdList=self.fdList, db=self.db)
    self.assertEqual(1, self.importer.licensesMapping.get("DoAnything", None))
    self.assertEqual(2, self.importer.licensesMapping.get("HarshEULA", None))
    self.assertEqual(None, self.importer.licensesMapping.get("UnknownLicense", None))

  def test_checker_returns_true_if_all_licenses_are_known(self):
    # fill in finalLicense, since we are skipping _applyConversions
    for fd in self.fdList:
      fd.finalLicense = fd.license
    retval = self.importer._checkFileDataListForLicenses(fdList=self.fdList,
      db=self.db)
    self.assertEqual(True, retval)

  def test_checker_returns_false_if_any_licenses_are_unknown(self):
    # fill in finalLicense, since we are skipping _applyConversions
    for fd in self.fdList:
      fd.finalLicense = fd.license
    self.fdList.append(self.fd5)
    retval = self.importer._checkFileDataListForLicenses(fdList=self.fdList,
      db=self.db)
    self.assertEqual(False, retval)

  def test_cannot_import_without_providing_valid_fdList(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    with self.assertRaises(ProjectDBInsertError):
      self.importer.importFileDataList(db=self.db, scan_id=self.scan_id)

  def test_cannot_import_without_providing_database(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    with self.assertRaises(ProjectDBInsertError):
      self.importer.importFileDataList(fdList=self.fdList,
        scan_id=self.scan_id)

  def test_cannot_import_without_providing_scan_id(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    with self.assertRaises(ProjectDBInsertError):
      self.importer.importFileDataList(fdList=self.fdList, db=self.db)

  def test_cannot_import_with_positional_args(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    with self.assertRaises(TypeError):
      self.importer.importFileDataList(self.fdList)
    with self.assertRaises(TypeError):
      self.importer.importFileDataList(self.fdList, self.db)
    with self.assertRaises(TypeError):
      self.importer.importFileDataList(self.fdList, self.db, self.scan_id)

  def test_checker_returns_true_if_all_paths_are_unique(self):
    retval = self.importer._checkFileDataListForDuplicatePaths(fdList=self.fdList)
    self.assertEqual(True, retval)

  def test_checker_returns_false_if_any_paths_are_duplicates(self):
    fdup = createFD("/tmp/f2", "DoAnythingNoncommercial", sha256="abcdef")
    self.fdList.append(fdup)
    retval = self.importer._checkFileDataListForDuplicatePaths(fdList=self.fdList)
    self.assertEqual(False, retval)

  def test_files_are_imported_if_all_is_good(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    retval = self.importer.importFileDataList(fdList=self.fdList, db=self.db,
      scan_id=self.scan_id)
    self.assertEqual(True, retval)
    f1 = self.db.getFile(scan_id=self.scan_id, path="/tmp/f1")
    self.assertEqual("/tmp/f1", f1.path)
    self.assertEqual("abcdef", f1.md5)
    self.assertEqual("DoAnything", f1.license.name)
    f4 = self.db.getFile(scan_id=self.scan_id, path="/tmp/f4")
    self.assertEqual("/tmp/f4", f4.path)
    self.assertEqual(None, f4.md5)
    self.assertEqual("HarshEULA", f4.license.name)

  def test_can_get_count_of_imported_files_if_all_licenses_are_known(self):
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.importer.importFileDataList(fdList=self.fdList, db=self.db,
      scan_id=self.scan_id)
    count = self.importer.getImportedCount()
    self.assertEqual(4, count)

  def test_files_are_not_imported_if_any_licenses_are_unknown(self):
    self.fdList.append(self.fd5)
    self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    with self.assertRaises(ProjectDBInsertError):
      self.importer.importFileDataList(fdList=self.fdList, db=self.db,
        scan_id=self.scan_id)
    f1 = self.db.getFile(scan_id=self.scan_id, path="/tmp/f1")
    self.assertIsNone(f1)

  def test_checker_applies_conversions(self):
    self.fdList.append(self.fdConvert)
    retval = self.importer.checkFileDataList(fdList=self.fdList, db=self.db)
    self.assertTrue(retval)
    self.assertEqual("293PageEULA", self.fdConvert.finalLicense)
