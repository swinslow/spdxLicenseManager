# tests/unit_tvparser.py
#
# Unit test for spdxLicenseManager: SPDX tag-value parser.
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

from slm.tvParser import TVParser, ParsedFileData

class TVParserTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX tag-value parser unit test suite."""

  def setUp(self):
    self.parser = TVParser()

  def tearDown(self):
    pass

  ##### Test cases below

  def test_new_parser_is_in_expected_reset_state(self):
    self.assertEqual(self.parser.state, self.parser.STATE_READY)
    self.assertEqual(self.parser.fdList, [])
    self.assertIsNone(self.parser.currentFileData)
    self.assertEqual(self.parser.errorMessage, "")

  @mock.patch('slm.tvParser.TVParser._parseNextPairFromReady')
  def test_will_call_correct_helper_for_ready_state(self, r_mock):
    self.parser.state = self.parser.STATE_READY
    self.parser.parseNextPair("tag", "value")
    r_mock.assert_called_with("tag", "value")

  @mock.patch('slm.tvParser.TVParser._parseNextPairFromMidfile')
  def test_will_call_correct_helper_for_midfile_state(self, m_mock):
    self.parser.state = self.parser.STATE_MIDFILE
    self.parser.parseNextPair("tag", "value")
    m_mock.assert_called_with("tag", "value")

  @mock.patch('slm.tvParser.TVParser._parseNextPairFromReady')
  @mock.patch('slm.tvParser.TVParser._parseNextPairFromMidfile')
  def test_will_not_call_helpers_for_error_state(self, m_mock, r_mock):
    self.parser.state = self.parser.STATE_ERROR
    self.parser.parseNextPair("tag", "value")
    m_mock.assert_not_called()
    r_mock.assert_not_called()

  @mock.patch('slm.tvParser.TVParser._parseNextPairFromReady')
  @mock.patch('slm.tvParser.TVParser._parseNextPairFromMidfile')
  def test_will_not_call_helpers_for_invalid_state(self, m_mock, r_mock):
    self.parser.state = 17
    self.parser.parseNextPair("tag", "value")
    m_mock.assert_not_called()
    r_mock.assert_not_called()

  def test_will_set_error_state_for_parse_in_invalid_state(self):
    self.parser.state = 17
    self.parser.parseNextPair("tag", "value")
    self.assertEqual(self.parser.STATE_ERROR, self.parser.state)
    self.assertEqual("Tag-value parser in invalid state for pair ('tag', 'value'): 17", self.parser.errorMessage)

  def test_filename_tag_in_ready_moves_to_midfile_state(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.assertEqual(self.parser.STATE_MIDFILE, self.parser.state)
    self.assertEqual(type(self.parser.currentFileData), ParsedFileData)
    self.assertEqual(self.parser.currentFileData.path, "/tmp/hi")
    self.assertEqual(self.parser.currentFileData.license, "")
    self.assertEqual(self.parser.currentFileData.md5, "")
    self.assertEqual(self.parser.currentFileData.sha1, "")
    self.assertEqual(self.parser.currentFileData.sha256, "")

  def test_non_filename_tag_in_ready_stays_in_ready_state(self):
    self.parser.parseNextPair("Whatever", "something else")
    self.assertEqual(self.parser.STATE_READY, self.parser.state)
    self.assertIsNone(self.parser.currentFileData)

  def test_can_extract_checksum_types(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser._parseFileChecksum("SHA1: abc123")
    self.assertEqual(self.parser.currentFileData.sha1, "abc123")
    self.parser._parseFileChecksum("MD5: def432")
    self.assertEqual(self.parser.currentFileData.md5, "def432")
    self.parser._parseFileChecksum("SHA256: 035183")
    self.assertEqual(self.parser.currentFileData.sha256, "035183")

  def test_error_for_invalid_short_filechecksum_format(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser._parseFileChecksum("blah")
    self.assertEqual(self.parser.STATE_ERROR, self.parser.state)
    self.assertEqual("Invalid FileChecksum format: 'blah'", self.parser.errorMessage)

  def test_error_for_invalid_long_filechecksum_format(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser._parseFileChecksum("MD5: 12390834: other")
    self.assertEqual(self.parser.STATE_ERROR, self.parser.state)
    self.assertEqual("Invalid FileChecksum format: 'MD5: 12390834: other'", self.parser.errorMessage)

  def test_error_for_unknown_filechecksum_type(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser._parseFileChecksum("ECDSA: 12390834")
    self.assertEqual(self.parser.STATE_ERROR, self.parser.state)
    self.assertEqual("Unknown FileChecksum type: 'ECDSA'", self.parser.errorMessage)

  def test_will_record_data_in_current_file_data(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser.parseNextPair("LicenseConcluded", "EULA")
    self.parser.parseNextPair("FileChecksum", "SHA1: abc123")
    self.parser.parseNextPair("FileChecksum", "MD5: 456789")
    self.parser.parseNextPair("FileChecksum", "SHA256: 0def12")
    self.assertEqual(self.parser.currentFileData.path, "/tmp/hi")
    self.assertEqual(self.parser.currentFileData.license, "EULA")
    self.assertEqual(self.parser.currentFileData.sha1, "abc123")
    self.assertEqual(self.parser.currentFileData.md5, "456789")
    self.assertEqual(self.parser.currentFileData.sha256, "0def12")

  def test_will_record_and_go_on_to_next_file_data(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser.parseNextPair("LicenseConcluded", "EULA")
    self.parser.parseNextPair("FileChecksum", "SHA1: abc123")
    self.parser.parseNextPair("FileChecksum", "MD5: 456789")
    self.parser.parseNextPair("FileChecksum", "SHA256: 0def12")
    self.parser.parseNextPair("FileName", "/tmp/bye")
    self.parser.parseNextPair("LicenseConcluded", "Unlicense")
    self.parser.parseNextPair("FileChecksum", "SHA1: cccccc")
    self.parser.parseNextPair("FileChecksum", "MD5: bbbbbb")
    self.parser.parseNextPair("FileChecksum", "SHA256: eeeeee")
    self.assertEqual(type(self.parser.fdList[0]), ParsedFileData)
    self.assertEqual(self.parser.fdList[0].path, "/tmp/hi")
    self.assertEqual(self.parser.fdList[0].license, "EULA")
    self.assertEqual(self.parser.fdList[0].sha1, "abc123")
    self.assertEqual(self.parser.fdList[0].md5, "456789")
    self.assertEqual(self.parser.fdList[0].sha256, "0def12")
    self.assertEqual(self.parser.currentFileData.path, "/tmp/bye")
    self.assertEqual(self.parser.currentFileData.license, "Unlicense")
    self.assertEqual(self.parser.currentFileData.sha1, "cccccc")
    self.assertEqual(self.parser.currentFileData.md5, "bbbbbb")
    self.assertEqual(self.parser.currentFileData.sha256, "eeeeee")

  def test_at_end_will_save_last_file_data(self):
    self.parser.parseNextPair("FileName", "/tmp/hi")
    self.parser.parseNextPair("LicenseConcluded", "EULA")
    self.parser.parseNextPair("FileChecksum", "SHA1: abc123")
    self.parser.parseNextPair("FileChecksum", "MD5: 456789")
    self.parser.parseNextPair("FileChecksum", "SHA256: 0def12")
    self.parser.finalize()
    self.assertEqual(type(self.parser.fdList[0]), ParsedFileData)
    self.assertEqual(self.parser.fdList[0].path, "/tmp/hi")
    self.assertEqual(self.parser.fdList[0].license, "EULA")
    self.assertEqual(self.parser.fdList[0].sha1, "abc123")
    self.assertEqual(self.parser.fdList[0].md5, "456789")
    self.assertEqual(self.parser.fdList[0].sha256, "0def12")
    self.assertIsNone(self.parser.currentFileData)
