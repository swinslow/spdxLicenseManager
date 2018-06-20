# tests/unit_dbapprovals.py
#
# Unit test for spdxLicenseManager: database functions for Approvals.
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

from slm.datatypes import (Approval, ApprovalType, Category, Component,
  ComponentLocation, ComponentType, File, License, Scan, Subproject)

class DBApprovalUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for approvals in DB."""

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
    self.insertSampleComponentTypeData()
    self.insertSampleComponentData()
    self.insertSampleComponentLocationData()
    self.insertSampleComponentLicenseData()
    self.insertSampleApprovalTypeData()

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
      License(_id=5, name="Apache-2.0", category_id=3),
      License(_id=6, name="CC-BY-4.0", category_id=3),
      License(_id=7, name="CC0-1.0", category_id=2),
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
      File(_id=1, scan_id=1, path="/fileC.c", license_id=1, sha1="aabbcc", md5="ddeeff", sha256="aaccee"),
      File(_id=2, scan_id=1, path="/fileA.c", license_id=1, sha1="112233", md5="445566", sha256="778899"),
      File(_id=3, scan_id=1, path="/fileB.c", license_id=2, sha1=None, md5=None, sha256=None),
      File(_id=4, scan_id=1, path="/dir/fileA.c", license_id=4, sha1="123456", md5="789012", sha256="345678"),
      File(_id=5, scan_id=1, path="/vendor/github.com/swinslow/peridot/file1.go", license_id=2),
      File(_id=6, scan_id=1, path="/vendor/github.com/swinslow/peridot/file2.go", license_id=2),
      File(_id=7, scan_id=1, path="/vendor/github.com/swinslow/peridot/file3.go", license_id=3),
      File(_id=8, scan_id=1, path="/vendor/github.com/swinslow/peridot/dir/subfile4.go", license_id=4),
      File(_id=9, scan_id=1, path="/magic.js", license_id=3),
      # and files from a second rescan
      File(_id=10, scan_id=2, path="/vendor/github.com/swinslow/peridot/file1.go", license_id=2),
      File(_id=11, scan_id=2, path="/vendor/github.com/swinslow/peridot/dir/subfile4.go", license_id=4),
      File(_id=12, scan_id=2, path="/magic.js", license_id=3),
      File(_id=13, scan_id=2, path="/notThisOne/magic.js", license_id=3),
      # and a file that is covered by two components, in the second rescan
      File(_id=14, scan_id=2, path="/magicAndPeridot.js", license_id=1),
    ]
    self.db.session.bulk_save_objects(files)
    self.db.session.commit()

  def insertSampleComponentTypeData(self):
    component_types = [
      ComponentType(_id=1, name="Python"),
      ComponentType(_id=2, name="JavaScript"),
      ComponentType(_id=3, name="Golang"),
    ]
    self.db.session.bulk_save_objects(component_types)
    self.db.session.commit()

  def insertSampleComponentData(self):
    components = [
      Component(_id=1, scan_id=1, component_type_id=3, name="github.com/swinslow/peridot"),
      Component(_id=2, scan_id=1, component_type_id=2, name="magic"),
      Component(_id=3, scan_id=2, component_type_id=3, name="github.com/swinslow/peridot"),
      Component(_id=4, scan_id=2, component_type_id=2, name="magic"),
      Component(_id=5, scan_id=1, component_type_id=1, name="spdxLicenseManager"),
    ]
    self.db.session.bulk_save_objects(components)
    self.db.session.commit()

  def insertSampleComponentLocationData(self):
    clics = [
      # absolute=False, so pick this up anywhere
      ComponentLocation(component_id=1, path="/github.com/swinslow/peridot/", absolute=False),
      # absolute=True, so only pick this up in the root directory
      ComponentLocation(component_id=2, path="/magic.js", absolute=True),
      ComponentLocation(component_id=3, path="/github.com/swinslow/peridot/", absolute=False),
      ComponentLocation(component_id=4, path="/magic.js", absolute=True),
      # and this file contains two components
      ComponentLocation(component_id=3, path="/magicAndPeridot.js", absolute=True),
      ComponentLocation(component_id=4, path="/magicAndPeridot.js", absolute=True),
    ]
    self.db.session.bulk_save_objects(clics)
    self.db.session.commit()

  def insertSampleComponentLicenseData(self):
    clics = [
      ComponentLicense(component_id=4, license_id=5),
      ComponentLicense(component_id=4, license_id=6),
      ComponentLicense(component_id=3, license_id=5),
      ComponentLicense(component_id=3, license_id=6),
      ComponentLicense(component_id=3, license_id=7),
    ]
    self.db.session.bulk_save_objects(clics)
    self.db.session.commit()
  
  def insertSampleApprovalTypeData(self):
    approval_types = [
      ApprovalType(_id=1, name="GB approval"),
      ApprovalType(_id=2, name="Whitelisted"),
      ApprovalType(_id=3, name="Previously approved"),
    ]
    self.db.session.bulk_save_objects(approval_types)
    self.db.session.commit()
  
  def insertSampleApprovalData(self):
    approvals = [
      Approval(_id=1, component_id=3, date=)
    ]

  ##### Test cases below

  def test_can_retrieve_approvals_for_one_scan(self):
    approvals = set.db.getApprovals(scan_id=1)