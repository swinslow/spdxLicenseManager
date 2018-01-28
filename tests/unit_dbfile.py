# tests/unit_dbfile.py
#
# Unit test for spdxLicenseManager: database functions for Files.
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

from slm.datatypes import Category, File, License, Scan, Subproject

class DBFileUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for scan metadata in DB."""

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

  def tearDown(self):
    self.db.closeDB()
    self.db = None

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

  def insertSampleFileData(self):
    files = [
      File(_id=1, scan_id=1, path="/fileC.c", license_id=1,
        sha1="aabbcc", md5="ddeeff", sha256="aaccee"),
      File(_id=2, scan_id=1, path="/fileA.c", license_id=1,
        sha1="112233", md5="445566", sha256="778899"),
      File(_id=3, scan_id=1, path="/fileB.c", license_id=2,
        sha1=None, md5=None, sha256=None),
      File(_id=4, scan_id=1, path="/dir/fileA.c", license_id=4,
        sha1="123456", md5="789012", sha256="345678"),
    ]
    self.db.session.bulk_save_objects(files)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_files_in_one_scan(self):
    files = self.db.getFiles(scan_id=1)
    self.assertIsInstance(files, list)
    self.assertEqual(len(files), 4)
    # will sort by file path
    self.assertEqual(files[0]._id, 4)
    self.assertEqual(files[0].path, "/dir/fileA.c")
    self.assertEqual(files[1]._id, 2)
    self.assertEqual(files[1].path, "/fileA.c")
    self.assertEqual(files[2]._id, 3)
    self.assertEqual(files[2].path, "/fileB.c")
    self.assertEqual(files[3]._id, 1)
    self.assertEqual(files[3].path, "/fileC.c")

  def test_cannot_retrieve_files_in_scan_that_does_not_exist(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFiles(scan_id=17)

  def test_returns_empty_list_if_no_files_in_known_scan(self):
    files = self.db.getFiles(scan_id=4)
    self.assertEqual(files, [])

  def test_can_get_file_by_id(self):
    file = self.db.getFile(_id=3)
    self.assertEqual(file.path, "/fileB.c")
    self.assertEqual(file.license.name, "HarshEULA")

  def test_can_get_file_by_scan_and_path(self):
    file = self.db.getFile(scan_id=1, path="/fileB.c")
    self.assertEqual(file._id, 3)
    self.assertEqual(file.license.name, "HarshEULA")

  def test_cannot_get_file_by_id_with_scan_or_path(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFile(_id=3, scan_id=1)
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFile(_id=3, path="/fileB.c")

  def test_cannot_get_file_with_no_id_or_scan_or_path(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFile()

  def test_cannot_get_file_with_only_one_of_scan_or_path(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFile(scan_id=1)
    with self.assertRaises(ProjectDBQueryError):
      self.db.getFile(path="/fileB.c")

  def test_returns_none_if_file_not_found_by_id(self):
    file = self.db.getFile(_id=17)
    self.assertIsNone(file)

  def test_returns_none_if_file_not_found_by_scan_plus_path(self):
    file = self.db.getFile(scan_id=1, path="/nope")
    self.assertIsNone(file)
    file = self.db.getFile(scan_id=6, path="/fileB.c")
    self.assertIsNone(file)

  def test_can_add_and_retrieve_files(self):
    self.db.addFile(scan_id=1, path="/file17.py", license_id=3,
      sha1=None, md5=None, sha256=None)
    self.db.addFile(scan_id=1, path="/file13.py", license_id=2,
      sha1=None, md5=None, sha256=None)
    file_id = self.db.addFile(scan_id=1, path="/dir5/file128.py", license_id=4,
      sha1="123456", md5="789012", sha256="345678")

    # confirm that we now have seven files in this scan
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 7)
    self.assertEqual(file_id, 7)

    # and confirm that we can retrieve this one by id
    file = self.db.getFile(_id=7)
    self.assertEqual(file.path, "/dir5/file128.py")
    self.assertEqual(file.license.name, "DoAnythingNoncommercial")

  def test_can_start_adding_but_rollback_file(self):
    file_id = self.db.addFile(scan_id=1, path="/will_rollback", license_id=3,
      sha1=None, md5=None, sha256=None, commit=False)
    self.db.rollback()
    # confirm that we still only have four files
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 4)
    # and confirm that this file ID doesn't exist in database
    file = self.db.getFile(_id=file_id)
    self.assertIsNone(file)

  def test_can_start_adding_and_then_commit_files(self):
    f1_id = self.db.addFile(scan_id=1, path="/f1", license_id=1,
      sha1=None, md5=None, sha256=None, commit=False)
    f2_id = self.db.addFile(scan_id=1, path="/f2", license_id=1,
      sha1=None, md5=None, sha256=None, commit=False)
    self.db.commit()
    # confirm that we now have six files
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 6)

  def test_can_bulk_add_and_retrieve_files(self):
    bulkfiles = [
      ("/file17.py", 3, None, None, None),
      ("/file13.py", 2, None, None, None),
      ("/dir5/file128.py", 4, "123456", "789012", "345678"),
    ]
    self.db.addBulkFiles(scan_id=1, file_tuples=bulkfiles)

    # confirm that we now have seven files in this scan
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 7)

    # and confirm that we can retrieve last one by id
    file = self.db.getFile(_id=7)
    self.assertEqual(file.path, "/dir5/file128.py")
    self.assertEqual(file.license.name, "DoAnythingNoncommercial")

  def test_can_start_bulk_adding_files_but_rollback(self):
    bulkfiles = [
      ("/file17.py", 3, None, None, None),
      ("/file13.py", 2, None, None, None),
      ("/dir5/file128.py", 4, "123456", "789012", "345678"),
    ]
    self.db.addBulkFiles(scan_id=1, file_tuples=bulkfiles, commit=False)
    self.db.rollback()
    # confirm that we still only have four files
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 4)
    # and confirm that this file ID doesn't exist in database
    file = self.db.getFile(_id=7)
    self.assertIsNone(file)

  def test_can_start_bulk_adding_and_then_commit_files(self):
    bulkfiles = [
      ("/file17.py", 3, None, None, None),
      ("/file13.py", 2, None, None, None),
      ("/dir5/file128.py", 4, "123456", "789012", "345678"),
    ]
    self.db.addBulkFiles(scan_id=1, file_tuples=bulkfiles, commit=False)
    self.db.commit()
    # confirm that we now have seven files
    files = self.db.getFiles(scan_id=1)
    self.assertEqual(len(files), 7)
