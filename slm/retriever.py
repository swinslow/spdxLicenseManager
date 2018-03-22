# retriever.py
#
# Module for spdxLicenseManager to check for SPDX files in a designated
# directory, and rename / move them into the appropriate subproject folder.
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

from datetime import datetime
import os

class RetrieverConfigError(Exception):
  """Exception raised for errors in SPDX retriever configuration.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class Retriever:

  def __init__(self):
    super(Retriever, self).__init__()
    self._reset()

  ##### Retriever configuration functions

  def addSubproject(self, spdx_search, _id):
    if (spdx_search is None or type(spdx_search) != str or spdx_search == ""):
      raise RetrieverConfigError("spdx_search must be a non-empty string")
    if (_id is None or type(_id) != int or _id < 1):
      raise RetrieverConfigError("_id must be a positive integer")
    self.subprojects[spdx_search] = (_id, [])

  def setDatestr(self, datestr):
    if datestr == "":
      self.datestr = ""
      return
    try:
      dt = datetime.strptime(datestr, "%Y-%m")
      self.datestr = datestr
    except ValueError:
      raise RetrieverConfigError(f"Cannot set date string to {datestr}; must be valid year and month in form YYYY-MM")

  def setSearchDir(self, search_dir):
    if not os.path.isdir(search_dir):
      raise RetrieverConfigError(f"{search_dir} is not an existing directory to search for SPDX files")
    self.search_dir = search_dir

  def setProjectDir(self, project_dir):
    if not os.path.isdir(project_dir):
      raise RetrieverConfigError(f"{project_dir} is not an existing SLM project directory")
    self.project_dir = project_dir

  ##### Other helper functions

  def _reset(self):
    self.subprojects = {}
    self.datestr = ""
    self.search_dir = ""
    self.project_dir = ""
    self.results = {}
