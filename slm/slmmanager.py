# slmmanager.py
#
# Module to manage file paths and status retrieval for SLM-managed
# projects, databases and reports.
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

class SLMManager():
  def __init__(self, config=None, root=""):
    super(SLMManager, self).__init__()
    self.config = config
    self.root = root

  def getProjects(self):
    return [cp.name for cp in self.config.projects]

  def getProjectDir(self, project):
    return os.path.join(self.root, "projects", project)

  def getProjectDBPath(self, project):
    dbFilename = project + ".db"
    return os.path.join(self.getProjectDir(project), dbFilename)

  def getProjectReportsDir(self, project):
    return os.path.join(self.getProjectDir(project), "reports")

  def getSubprojectDir(self, project, subproject):
    return os.path.join(self.getProjectDir(project), "subprojects", subproject)

  def getSubprojectReportsDir(self, project, subproject):
    return os.path.join(self.getSubprojectDir(project, subproject), "reports")

  def getSubprojectSPDXDir(self, project, subproject):
    return os.path.join(self.getSubprojectDir(project, subproject), "spdx")
