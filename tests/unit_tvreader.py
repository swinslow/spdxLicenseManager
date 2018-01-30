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

  @mock.patch('slm.tvReader.TVReader._readNextLineFromReady')
  def test_will_call_correct_helper_for_ready_state(self, ready_mock):
    self.reader.state = self.reader.STATE_READY
    self.reader.readNextLine("test")
    ready_mock.assert_called_with("test")

  @mock.patch('slm.tvReader.TVReader._readNextLineFromMidtext')
  def test_will_call_correct_helper_for_midtext_state(self, midtext_mock):
    self.reader.state = self.reader.STATE_MIDTEXT
    self.reader.readNextLine("test")
    midtext_mock.assert_called_with("test")

  @mock.patch('slm.tvReader.TVReader._readNextLineFromReady')
  @mock.patch('slm.tvReader.TVReader._readNextLineFromMidtext')
  def test_will_not_call_helpers_for_error_state(self, m_mock, r_mock):
    self.reader.state = self.reader.STATE_ERROR
    self.reader.readNextLine("test")
    m_mock.assert_not_called()
    r_mock.assert_not_called()

  @mock.patch('slm.tvReader.TVReader._readNextLineFromReady')
  @mock.patch('slm.tvReader.TVReader._readNextLineFromMidtext')
  def test_will_not_call_helpers_for_read_in_invalid_state(self, m_mock, r_mock):
    self.reader.state = 17
    self.reader.readNextLine("test")
    m_mock.assert_not_called()
    r_mock.assert_not_called()

  def test_will_set_error_state_for_read_in_invalid_state(self):
    self.reader.state = 17
    self.reader.readNextLine("test")
    self.assertEqual(self.reader.STATE_ERROR, self.reader.state)

  def test_current_line_increases_on_each_read_call(self):
    self.reader.readNextLine("Tag: value")
    self.assertEqual(1, self.reader.currentLine)
    self.reader.currentLine = 23
    self.reader.readNextLine("Tag: value")
    self.assertEqual(24, self.reader.currentLine)

  def test_helper_will_reset_current_tag_and_value(self):
    self.reader.currentTag = "hi"
    self.reader.currentValue = "there"
    self.reader._resetCurrentTagValue()
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_can_read_single_tag_value(self):
    self.reader.readNextLine("Tag:value")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])
    self.assertEqual(self.reader.currentLine, 1)
    # it doesn't adjust currentTag or currentValue b/c we aren't mid-<text>
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_can_strip_whitespace_from_value(self):
    self.reader.readNextLine("Tag:   value  ")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])

  def test_ready_cannot_read_line_with_no_colon(self):
    self.reader.readNextLine("No colon is an error")
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.state, self.reader.STATE_ERROR)

  def test_ready_text_tag_switches_to_midtext_state(self):
    self.reader.readNextLine("Tag: <text>This begins a multiline value")
    self.assertEqual(self.reader.state, self.reader.STATE_MIDTEXT)
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "Tag")
    self.assertEqual(self.reader.currentValue, "This begins a multiline value")
    # nothing is added to the tag-value list until we close the <text> value
    self.assertEqual(self.reader.tvList, [])

  def test_ready_text_tag_and_closing_tag_in_one_line_finishes_read(self):
    self.reader.readNextLine("Tag: <text>Just one line</text>")
    self.assertEqual(self.reader.state, self.reader.STATE_READY)
    self.assertEqual(self.reader.tvList, [("Tag", "Just one line")])
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_midtext_continues_if_no_closing_text(self):
    self.reader.state = self.reader.STATE_MIDTEXT
    self.reader.currentTag = "Multiline"
    self.reader.currentValue = "First line\n"
    self.reader.readNextLine("Second line")
    # should still be in midtext
    self.assertEqual(self.reader.state, self.reader.STATE_MIDTEXT)
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.currentTag, "Multiline")
    self.assertEqual(self.reader.currentValue, "First line\nSecond line\n")

  def test_midtext_finishes_if_reaching_closing_text(self):
    self.reader.state = self.reader.STATE_MIDTEXT
    self.reader.currentTag = "Multiline"
    self.reader.currentValue = "First line\n"
    self.reader.readNextLine("Second line</text>")
    # should finish and go back to ready, without final line break
    self.assertEqual(self.reader.state, self.reader.STATE_READY)
    self.assertEqual(self.reader.tvList, [("Multiline", "First line\nSecond line")])
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_ignores_comment_lines(self):
    self.reader.readNextLine("# this is a comment")
    self.assertEqual(self.reader.state, self.reader.STATE_READY)
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_midtext_includes_comment_lines(self):
    self.reader.state = self.reader.STATE_MIDTEXT
    self.reader.currentTag = "Multiline"
    self.reader.currentValue = "First line\n"
    self.reader.readNextLine("# This is part of multiline text")
    # should still be in midtext
    self.assertEqual(self.reader.state, self.reader.STATE_MIDTEXT)
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.currentTag, "Multiline")
    self.assertEqual(self.reader.currentValue, "First line\n# This is part of multiline text\n")

  def test_ready_ignores_spaces_before_tag(self):
    self.reader.readNextLine("      Tag:value")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_ignores_spaces_before_comment_lines(self):
    self.reader.readNextLine("         # this is a comment")
    self.assertEqual(self.reader.state, self.reader.STATE_READY)
    self.assertEqual(self.reader.tvList, [])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_ignores_spaces_between_tag_and_colon(self):
    self.reader.readNextLine("Tag     :value")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_ignores_spaces_between_colon_and_value(self):
    self.reader.readNextLine("Tag:      value")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_ready_ignores_spaces_after_end_of_value(self):
    self.reader.readNextLine("Tag:value     ")
    self.assertEqual(self.reader.tvList, [("Tag", "value")])
    self.assertEqual(self.reader.currentLine, 1)
    self.assertEqual(self.reader.currentTag, "")
    self.assertEqual(self.reader.currentValue, "")

  def test_can_check_whether_in_error_state(self):
    self.assertFalse(self.reader.isError())
    self.reader.state = self.reader.STATE_ERROR
    self.assertTrue(self.reader.isError())
