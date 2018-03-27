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
import shutil

class RetrieverConfigError(Exception):
  """Exception raised for errors in SPDX retriever configuration.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class RetrieverNotReadyError(Exception):
  """Exception raised for errors in SPDX retriever order of operations.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class Retriever:

  def __init__(self):
    super(Retriever, self).__init__()
    self._reset()

  ##### Retriever main functions

  def prepareFiles(self):
    if self.filesPrepared == True:
      raise RetrieverNotReadyError("Cannot call prepareFiles again on this Retriever")
    if self.subprojects == {}:
      raise RetrieverNotReadyError("No subprojects added before call to prepareFiles")
    if self.search_dir == "":
      raise RetrieverNotReadyError("Search directory not set before call to prepareFiles")
    if self.datestr == "":
      raise RetrieverNotReadyError("Date string not set before call to prepareFiles")

    files = self._getFiles(self.search_dir)
    for file in files:
      filepath = os.path.join(self.search_dir, file)
      for spdx_search in self.subprojects.keys():
        if self._testFilename(filepath, spdx_search, self.datestr):
          t = self.subprojects[spdx_search]
          t[2].append(filepath)
    self.filesPrepared = True

  def createResults(self):
    if self.results != {}:
      raise RetrieverNotReadyError("Cannot call createResults again on this Retriever")
    if self.project_dir == "":
      raise RetrieverNotReadyError("Project directory not set before call to createResults")

    self.results["success"] = []
    self.results["error"] = []
    for spdx_search, (name, _id, matches) in self.subprojects.items():
      if len(matches) == 1:
        dstFilename = self._makeDstFilename(
          srcPath = matches[0],
          spdx_search = spdx_search,
          datestr = self.datestr,
          subproject_name = name
        )
        dstPath = os.path.join(self.project_dir, name, "spdx", dstFilename)
        self.results["success"].append((_id, name, matches[0], dstPath))
      elif len(matches) == 0:
        self.results["error"].append((_id, name, f'No matches found for project {name} (with string "{spdx_search}")'))
      else:
        filelistStr = ""
        for filepath in sorted(matches):
          filelistStr = filelistStr + "\n  " + filepath
        self.results["error"].append((_id, name, f'Multiple valid matches found for project {name} (with string "{spdx_search}"):{filelistStr}'))

  def moveFiles(self):
    if self.results == {}:
      raise RetrieverNotReadyError("Cannot call moveFiles on this Retriever before successfully calling createResults")
    success = self.results.get("success", [])
    newSuccess = []
    for _id, project, srcPath, dstPath in success:
      if os.path.isfile(dstPath):
        t = (_id, project, f'Cannot move to project {project} (file already present at {dstPath})')
        self.results["error"].append(t)
      else:
        shutil.move(srcPath, dstPath)
        t = (_id, project, srcPath, dstPath)
        newSuccess.append(t)
    self.results["success"] = newSuccess

  ##### Retriever helper functions

  def _testFilename(self, filename, spdx_search, datestr):
    # check that the filename extension is .spdx
    ext = os.path.splitext(filename)[1]
    if ext != ".spdx":
      return False
    # check that the subproject's search string is present in the filename
    spdxSearchLoc = filename.find(spdx_search)
    if spdxSearchLoc == -1:
      return False
    # check that the date string is also present
    dateLoc = filename.find(datestr)
    if dateLoc == -1:
      return False
    # check that the FULL date string (including day) is present and valid
    dateToCheck = filename[dateLoc:dateLoc+10]
    try:
      dt = datetime.strptime(dateToCheck, "%Y-%m-%d")
    except ValueError as e:
      return False
    return True

  def _getFiles(self, search_dir):
    files = []
    for pathname in os.listdir(search_dir):
      if os.path.isfile(os.path.join(search_dir, pathname)):
        files.append(pathname)
    return files

  def _makeDstFilename(self, srcPath, spdx_search, datestr, subproject_name):
    # find day in date
    # first, check that the date string is present
    dateLoc = srcPath.find(datestr)
    if dateLoc == -1:
      raise RetrieverNotReadyError(f"Date string {datestr} not found in source path {srcPath}")
    # check that the FULL date string (including day) is present and valid
    dateToCheck = srcPath[dateLoc:dateLoc+10]
    try:
      dt = datetime.strptime(dateToCheck, "%Y-%m-%d")
    except ValueError as e:
      raise RetrieverNotReadyError(f"Invalid date string {datestr} found in source path {srcPath}")

    daystr = dateToCheck[8:10]
    filename = f"{subproject_name}-{datestr}-{daystr}.spdx"
    return filename

  ##### Retriever configuration functions

  def addSubproject(self, name, spdx_search, _id):
    if (spdx_search is None or type(spdx_search) != str or spdx_search == ""):
      raise RetrieverConfigError("spdx_search must be a non-empty string")
    if (_id is None or type(_id) != int or _id < 1):
      raise RetrieverConfigError("_id must be a positive integer")
    self.subprojects[spdx_search] = (name, _id, [])

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
    self.filesPrepared = False
    self.results = {}
