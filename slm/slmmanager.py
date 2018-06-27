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
from datetime import datetime

from .projectdb import ProjectDB, ProjectDBConfigError

class SLMManagerError(Exception):
  """Exception raised for errors related to the SLM manager.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

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

  def openProjectDB(self, project):
    # find and open database for this project
    dbPath = self.getProjectDBPath(project)
    db = ProjectDB()
    db.openDB(dbPath)
    return db

  def getProjectReportsDir(self, project):
    return os.path.join(self.getProjectDir(project), "reports")

  def getSubprojectDir(self, project, subproject):
    return os.path.join(self.getProjectDir(project), "subprojects", subproject)

  def getSubprojectReportsDir(self, project, subproject):
    return os.path.join(self.getSubprojectDir(project, subproject), "reports")

  def getSubprojectSPDXDir(self, project, subproject):
    return os.path.join(self.getSubprojectDir(project, subproject), "spdx")

  def getSPDXPath(self, project, subproject, date_str):
    spdx_dir = self.getSubprojectSPDXDir(project, subproject)
    filename = f"{subproject}-{date_str}.spdx"
    return os.path.join(spdx_dir, filename)

  def getScanDates(self, db, subproject, year_month):
    if subproject == None:
      raise SLMManagerError("No subproject specified")

    # check subproject
    sp = db.getSubproject(name=subproject)
    if sp == None:
      raise SLMManagerError("Unknown subproject name")

    # parse date-time
    dt = datetime.strptime(year_month, "%Y-%m")
    tup = (dt.year, dt.month)

    scans = db.getScansFiltered(subproject=subproject, month_tuple=tup)
    scan_dts = [datetime.strftime(scan.scan_dt, "%Y-%m-%d") for scan in scans]
    return sorted(scan_dts)

  def isScanForMonth(self, db, subproject, year_month):
    scan_dts = self.getScanDates(db, subproject, year_month)
    return len(scan_dts) > 0

  def getSPDXExpectedPaths(self, db, project, subproject, year_month):
    scan_dts = self.getScanDates(db, subproject, year_month)
    return [self.getSPDXPath(project, subproject, scan_dt) for scan_dt in scan_dts]

  def isSPDXForMonth(self, db, project, subproject, year_month):
    retval = False
    expectedPaths = self.getSPDXExpectedPaths(db, project, subproject, year_month)
    for ep in expectedPaths:
      if os.path.isfile(ep):
        retval = True
    return retval

  def isXLSXForMonth(self, project, subproject, year_month):
    retval = False
    repDir = self.getSubprojectReportsDir(project, subproject)
    expectedPaths = [os.path.join(repDir, f"{subproject}-{year_month}-{str(day).zfill(2)}.xlsx") for day in range(1, 32)]
    for ep in expectedPaths:
      if os.path.isfile(ep):
        retval = True
    return retval

  def isJSONForMonth(self, project, subproject, year_month):
    retval = False
    repDir = self.getSubprojectReportsDir(project, subproject)
    expectedPaths = [os.path.join(repDir, f"{subproject}-{year_month}-{str(day).zfill(2)}.json") for day in range(1, 32)]
    for ep in expectedPaths:
      if os.path.isfile(ep):
        retval = True
    return retval
