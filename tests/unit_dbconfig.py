# tests/unit_dbconfig.py
#
# Unit test for spdxLicenseManager: database functions for Configs.
#
# Copyright (C) The Linux Foundation
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
#
# SPDX-License-Identifier: Apache-2.0

import os
import unittest
from unittest import mock

from slm.projectdb import (ProjectDB, ProjectDBQueryError,
  ProjectDBInsertError, ProjectDBUpdateError)

from slm.datatypes import Config

class DBConfigUnitTestSuite(unittest.TestCase):
  """spdxLicenseManager unit test suite for configuration data in DB."""

  def setUp(self):
    # create and initialize an in-memory database
    self.db = ProjectDB()
    self.db.createDB(":memory:")
    self.db.initializeDBTables()

    # insert sample data
    self.insertSampleConfigData()

  def tearDown(self):
    self.db.closeDB()
    self.db = None

  def insertSampleConfigData(self):
    configs = [
      Config(key="strip_LicenseRef", value="yes"),
      Config(key="vendor_dirs", value="vendor;thirdparty;third-party"),
    ]
    self.db.session.bulk_save_objects(configs)
    self.db.session.commit()

  ##### Test cases below

  def test_can_retrieve_config_value_from_key(self):
    value = self.db.getConfigValue(key="strip_LicenseRef")
    self.assertEqual(value, "yes")

  def test_cannot_retrieve_config_value_for_unknown_key(self):
    with self.assertRaises(ProjectDBQueryError):
      self.db.getConfigValue(key="unknown_key")

  def test_can_set_and_get_config_value_for_new_key_if_known(self):
    self.db.setConfigValue(key="ignore_extensions", value="json")
    value = self.db.getConfigValue(key="ignore_extensions")
    self.assertEqual(value, "json")

  def test_can_update_and_get_config_value_for_existing_key(self):
    self.db.setConfigValue(key="vendor_dirs", value="vendor")
    value = self.db.getConfigValue(key="vendor_dirs")
    self.assertEqual(value, "vendor")

  def test_cannot_update_config_value_for_reserved_keys(self):
    with self.assertRaises(ProjectDBUpdateError):
      self.db.setConfigValue(key="magic", value="blah")
    with self.assertRaises(ProjectDBUpdateError):
      self.db.setConfigValue(key="initialized", value="blah")

  def test_cannot_set_unknown_key(self):
    with self.assertRaises(ProjectDBInsertError):
      self.db.setConfigValue(key="new_key", value="123abc")