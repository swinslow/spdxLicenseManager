# commands/cmdCreate.py
#
# Implementation of 'create-project' and 'create-subproject' commands for
# spdxLicenseManager.
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
import sys
import click

from .helperContext import extractContext
from ..projectdb import ProjectDB

def createNewProjectDirs(slmhome, pname):
  dirPath = os.path.abspath(os.path.join(slmhome, "projects", pname))
  os.makedirs(name=dirPath, mode=0o755)

def createNewProjectReportsDir(slmhome, pname):
  reportsDirPath = os.path.abspath(os.path.join(
    slmhome, "projects", pname, "reports"))
  os.makedirs(name=reportsDirPath, mode=0o755)

def createNewProjectSubprojectsDir(slmhome, pname):
  subprojectsDirPath = os.path.abspath(os.path.join(
    slmhome, "projects", pname, "subprojects"))
  os.makedirs(name=subprojectsDirPath, mode=0o755)

def createNewSubprojectDirs(slmhome, pname, spname):
  dirPath = os.path.abspath(os.path.join(
    slmhome, "projects", pname, "subprojects", spname))
  os.makedirs(name=dirPath, mode=0o755)

def createNewSubprojectReportsDir(slmhome, pname, spname):
  reportsDirPath = os.path.abspath(os.path.join(
    slmhome, "projects", pname, "subprojects", spname, "reports"))
  os.makedirs(name=reportsDirPath, mode=0o755)

def createNewSubprojectSPDXDir(slmhome, pname, spname):
  spdxDirPath = os.path.abspath(os.path.join(
    slmhome, "projects", pname, "subprojects", spname, "spdx"))
  os.makedirs(name=spdxDirPath, mode=0o755)

def cmdCreateProject(ctx, pname, pdesc):
  slmhome = ctx.obj.get('SLMHOME', None)
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  project = ctx.obj.get('PROJECT', None)

  # confirm didn't also pass in an existing project name
  if project is not None:
    # error, shouldn't call create-project and also pass a project name
    sys.exit(f"Error: called create-project but passed project={project}; did you mean to call create-subproject?")

  # confirm project doesn't already exist in SLM configuration file
  if mainconfig.getProjectDesc(pname) is not None:
    # error, shouldn't call create-project with existing name
    sys.exit(f"Error: project {pname} already exists")

  # create subdirectory for new project
  createNewProjectDirs(slmhome, pname)
  createNewProjectReportsDir(slmhome, pname)
  createNewProjectSubprojectsDir(slmhome, pname)

  # update main SLM config object
  mainconfig.addProject(pname, pdesc)

  # get and output new SLM config JSON
  newJSON = mainconfig.getJSON()
  mainconfigPath = os.path.join(slmhome, "slmconfig.json")
  with open(mainconfigPath, "w") as f:
    f.write(newJSON)

  # create new empty, initialized project database and write to disk
  db = ProjectDB()
  dbFilename = f"{pname}.db"
  dbPath = os.path.abspath(os.path.join(slmhome,
    "projects", pname, dbFilename))
  db.createDB(dbPath)
  db.initializeDBTables()
  db.closeDB()

def cmdCreateSubproject(ctx, spname, spdesc):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm did also pass in an existing project name
  if project is None:
    # error, shouldn't call create-subproject without a project name
    sys.exit("Error: called create-subproject but didn't pass a project name; did you mean to call create-project?")

  # confirm subproject doesn't already exist for this project
  if db.getSubproject(name=spname) is not None:
    # error, shouldn't call create-subproject with existing name
    sys.exit(f"Error: subproject {spname} already exists for project {project}")

  # create subdirectory for new subproject
  createNewSubprojectDirs(slmhome, project, spname)
  createNewSubprojectReportsDir(slmhome, project, spname)
  createNewSubprojectSPDXDir(slmhome, project, spname)

  # update project config object
  db.addSubproject(spname, spdesc)

  db.closeDB()

