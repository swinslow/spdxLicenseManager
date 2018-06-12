# reports/json.py
#
# Module for JSON report generation functions for spdxLicenseManager.
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

import json
import os

from .common import ReportFileError, ReportNotReadyError
from ..datatypes import Category, File, License

class JSONReporter:

  def __init__(self, db, config={}):
    super(JSONReporter, self).__init__()
    self._reset()
    self.db = db
    # copy over config entries into new dict
    for key, value in config.items():
      self.kwConfig[key] = value

  ##### Main JSON reporting functions
  ##### External usage shouldn't require calling anything except these

  def setResults(self, results):
    self.rjs = ""
    self.results = results

  def generate(self):
    pass

  def save(self, path, replace=False):
    if type(self.results) != list:
      raise ReportNotReadyError("Cannot call generateAndSave() before analysis results are set")

    self._saveCheck(path=path, replace=replace)

    try:
      with open(path, "w") as f:
        json.dump(list(self.results), f, cls=self.SLMJSONEncoder)
    except PermissionError:
      raise ReportFileError(f"Permission denied to save to {path}")

  ##### custom JSON encoder for relevant SLM data types

  class SLMJSONEncoder(json.JSONEncoder):
    def default(self, o):
      if isinstance(o, Category):
        return {
          'name': o.name,
          '_id': o._id,
          'licenses': o.licenses,
          'numFiles': self._getNumFilesForCategory(o),
        }
      elif isinstance(o, License):
        return {
          'name': o.name,
          '_id': o._id,
          'files': o.files,
          'numFiles': self._getNumFilesForLicense(o),
        }
      elif isinstance(o, File):
        if o.findings != {}:
          return {
            'path': o.path,
            '_id': o._id,
            'findings': o.findings,
            }
        else:
          return {
            'path': o.path,
            '_id': o._id,
          }
      else:
        print(o)
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}

    def _getNumFilesForLicense(self, lic):
      return len(lic.files)

    def _getNumFilesForCategory(self, cat):
      count = 0
      for lic in cat.licenses:
        count += self._getNumFilesForLicense(lic)
      return count

  ##### Helper functions for JSON saving

  def _saveCheck(self, path, replace=False):
    if type(self.results) != list:
      raise ReportNotReadyError("Cannot call generateAndSave() before analysis results are set")

    # check whether requested file already exists
    if os.path.exists(path) and not replace:
      raise ReportFileError(f"File already exists at {path}")

    # check whether we have write permission for this path
    if not os.access(path=os.path.dirname(path), mode=os.W_OK):
      raise ReportFileError(f"Permission denied to save to {path}")

  ##### Other helper functions

  def _reset(self):
    self.rjs = None
    self.results = None
    self.reportSaved = False
    self.kwConfig = {}

  def _getFinalConfigValue(self, key):
    kwValue = self.kwConfig.get(key, None)
    if kwValue is not None:
      return str(kwValue).lower()
    try:
      value = self.db.getConfigValue(key)
      return str(value).lower()
    except ProjectDBQueryError:
      return ""
