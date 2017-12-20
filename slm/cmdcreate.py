# cmdcreate.py
#
# Implementation of 'create' command for spdxLicenseManager.
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

import os
import sys
import click

from .projectconfig import ProjectConfig

def createNewProjectDirs(slmhome, pname):
  dirPath = os.path.abspath(os.path.join(slmhome, "projects", pname))
  os.makedirs(name=dirPath, mode=0o755)

def cmdcreateProject(ctx, pname, pdesc):
  slmhome = ctx.obj.get('SLMHOME', None)
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  project = ctx.obj.get('PROJECT', None)

  # confirm didn't also pass in an existing project name
  if project is not None:
    # error, shouldn't call create-project and also pass a project name
    sys.exit(f"Error: called create-project but passed project={project}; did you mean to call create-subproject?")

  # confirm project doesn't already exist
  if mainconfig.getProjectDesc(pname) is not None:
    # error, shouldn't call create-project with existing name
    sys.exit(f"Error: project {pname} already exists")

  # create subdirectory for new project
  createNewProjectDirs(slmhome, pname)

  # update main SLM config object
  mainconfig.addProject(pname, pdesc)

  # get and output new SLM config JSON
  newJSON = mainconfig.getJSON()
  mainconfigPath = os.path.join(slmhome, "slmconfig.json")
  with open(mainconfigPath, "w") as f:
    f.write(newJSON)

  # create new empty project config and write JSON to disk
  prjconfig = ProjectConfig()
  prjFilename = f"{pname}.config.json"
  prjconfigPath = os.path.join(slmhome, "projects", pname, prjFilename)
  prjJSON = prjconfig.getJSON()
  with open(prjconfigPath, "w") as f:
    f.write(prjJSON)

def cmdcreateSubproject(ctx):
  pass
