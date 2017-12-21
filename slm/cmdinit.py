# cmdinit.py
#
# Implementation of 'init' command for spdxLicenseManager.
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
import os
import sys
import click

def createNewHomeDir(newhome):
  dirPath = newhome
  os.makedirs(name=dirPath, mode=0o755)

def createNewProjectsDir(newhome):
  projectsPath = os.path.join(newhome, "projects")
  os.makedirs(name=projectsPath, mode=0o755)

def cmdinit(ctx, newhome):
  verbose = ctx.obj.get('VERBOSE', False)

  # check whether this is already an existing SLM directory
  # (e.g., does it have an slmconfig.json file and/or a projects directory?)
  homePath = os.path.abspath(newhome)
  if os.path.isdir(os.path.join(homePath, "projects")) or os.path.isfile(os.path.join(homePath, "slmconfig.json")):
    sys.exit(f"Error: {homePath} already appears to be an spdxLicenseManager directory.\nIf you REALLY want to re-initialize it, delete the entire directory and re-run this command.")

  # create new dirs
  createNewHomeDir(homePath)
  createNewProjectsDir(homePath)

  # create JSON config file with just a "projects" key
  # convert projects from tuples to dicts
  rep = {"projects": []}
  newJSON = json.dumps(rep, indent=2)
  mainconfigPath = os.path.join(newhome, "slmconfig.json")
  with open(mainconfigPath, "w") as f:
    f.write(newJSON)
