# tests/unit_tvreader.py
#
# Unit test for spdxLicenseManager: SPDX tag-value reader.
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

import unittest
from unittest import mock

from slm.tvReader import TVReader

class TVReaderTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX tag-value reader unit test suite."""

  def setUp(self):
    self.reader = TVReader()

  def tearDown(self):
    pass

  ##### Test cases below

  def test_new_reader_is_in_expected_reset_state(self):
    self.assertEqual(self.reader.state, self.reader.STATE_READY)
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.currentLine, 0)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  @mock.patch('slm.tvReader.TVReader._parseNextLineFromReady')
  def test_will_call_correct_helper_for_ready_state(self, ready_mock):
    self.reader.state = self.reader.STATE_READY
    self.reader.parseNextLine("test")
    ready_mock.assert_called_with("test")

  @mock.patch('slm.tvReader.TVReader._parseNextLineFromMidtext')
  def test_will_call_correct_helper_for_midtext_state(self, midtext_mock):
    self.reader.state = self.reader.STATE_MIDTEXT
    self.reader.parseNextLine("test")
    midtext_mock.assert_called_with("test")
