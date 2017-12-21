# projectconfig.py
#
# Module to load, parse and edit project configuration files for
# spdxLicenseManager.
#
# Copyright (C) 2017 The Linux Foundation
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

import json
import collections

class BadProjectConfigError(Exception):
  """Exception raised for errors in Project configuration.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

ProjectConfigSubproject = collections.namedtuple(
  'ProjectConfigSubproject',
  ['name', 'desc']
)

class ProjectConfig:
  def __init__(self):
    self.loaded = False
    self.subprojects = []

  def loadConfig(self, jsondata):
    jd = json.loads(jsondata)

    # load list of subprojects
    sps = jd.get("subprojects", [])
    for sp in sps:
      spname = sp.get("name", None)
      spdesc = sp.get("desc", "NO DESCRIPTION")
      if spname is None:
        raise BadProjectConfigError("No project name given")

      # check if name already present
      for spcheck in self.subprojects:
        if spname == spcheck.name:
          raise BadProjectConfigError(f"Subproject {spname} present multiple times in JSON for this project")

      # create tuple and add to list
      sptup = ProjectConfigSubproject(spname, spdesc)
      self.subprojects.append(sptup)

    # sort tuples by subproject name before returning
    self.subprojects.sort(key=lambda sp: sp.name)

    return len(self.subprojects)

  def getJSON(self):
    # convert subrojects from tuples to dicts
    subproject_rep = []
    for sp in self.subprojects:
      spd = {"name": sp.name, "desc": sp.desc}
      subproject_rep.append(spd)
    rep = {"subprojects": subproject_rep}
    return json.dumps(rep, indent=2)

  def getSubprojectDesc(self, spname):
    for sp in self.subprojects:
      if spname == sp.name:
        return sp.desc
    return None

  def addSubproject(self, spname, spdesc):
    # check if name already present
    for sp in self.subprojects:
      if spname == sp.name:
        raise BadProjectConfigError(f"Subproject {spname} already present for this project")

    sptup = ProjectConfigSubproject(spname, spdesc)
    self.subprojects.append(sptup)

    # sort tuples by subproject name before returning
    self.subprojects.sort(key=lambda sp: sp.name)

    return len(self.subprojects)

