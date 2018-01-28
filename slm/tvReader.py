# tvReader.py
#
# Module to read SPDX tag-value files and create a corresponding tag-value
# list, for spdxLicenseManager to subsequently parse into files and licenses.
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

class TVReader:
  # Possible reader state values
  # ready to parse new tag/value pair
  STATE_READY = 1
  # in the middle of parsing a multi-line <text> value
  STATE_MIDTEXT = 2
  # encountered an error from which we can't recover
  STATE_ERROR = 99

  def __init__(self):
    super(TVReader, self).__init__()
    self.reset()

  def reset(self):
    self.state = self.STATE_READY
    self.tvList = []
    self.currentLine = 0
    self.currentTag = ""
    self.currentValue = ""

  def _parseNextLineFromReady(self, line):
    pass

  def _parseNextLineFromMidtext(self, line):
    pass

  def parseNextLine(self, line):
    if self.state == self.STATE_READY:
      self._parseNextLineFromReady(line)
    elif self.state == self.STATE_MIDTEXT:
      self._parseNextLineFromMidtext(line)
