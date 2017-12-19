# slmconfig.py
#
# Module to load, parse and edit configuration files for spdxLicenseManager.
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

class BadSLMConfigError(Exception):
  def __init__(self, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)

SLMConfigProject = collections.namedtuple(
  'SLMConfigProject',
  ['name', 'desc']
)

class SLMConfig:
  def __init__(self):
    self.loaded = False
    self.projects = []

  def loadConfig(self, jsondata):
    jd = json.loads(jsondata)

    # load list of projects
    ps = jd.get("projects", [])
    for p in ps:
      pname = p.get("name", None)
      pdesc = p.get("desc", "=== NO DESCRIPTION ===")
      if pname is None:
        raise BadSLMConfigError

      # create tuple and add to list
      ptup = SLMConfigProject(pname, pdesc)
      self.projects.append(ptup)

    return len(self.projects)

  def getProjectDesc(self, pname):
    for p in self.projects:
      if pname == p.name:
        return p.desc
    return None
