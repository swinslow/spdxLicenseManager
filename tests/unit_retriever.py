# tests/unit_retriever.py
#
# Unit test for spdxLicenseManager: retrieving SPDX files.
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

from slm.retriever import Retriever
from slm.datatypes import Subproject

class RetrieverTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX retrieval unit test suite."""

  def setUp(self):
    # create retriever object
    self.retriever = Retriever()

  def tearDown(self):
    pass

  ##### Test cases below

  def test_new_retriever_is_in_expected_reset_state(self):
    self.assertEqual(self.retriever.subprojects, [])
    self.assertEqual(self.retriever.datestr, "")
    self.assertEqual(self.retriever.search_dir, "")
    self.assertEqual(self.retriever.project_dir, "")
    self.assertEqual(self.retriever.results, {})
