# tests/helper_sandbox.py
#
# Helper for spdxLicenseManager: set up default sandbox for functional tests.
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
import shutil
from testfixtures import TempDirectory

from slm.projectdb import ProjectDB
from slm.datatypes import Subproject

def setUpSandbox(testCase):
  # set up initial temp directory
  testCase.td = TempDirectory()

  # get paths to sandbox image and temp destination
  sandbox_src_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sandbox"
  )
  sandbox_dst_path = os.path.join(testCase.td.path, "sandbox")

  # copy subdirectories and contents
  shutil.copytree(sandbox_src_path, sandbox_dst_path)

  # set slmhome variable for test case
  testCase.slmhome = sandbox_dst_path

def tearDownSandbox(testCase):
  testCase.td.cleanup()

def runcmd(testCase, cli, project, *commands):
  elements = [f'--slmhome={testCase.slmhome}']
  if project is not None:
    elements.append(f'--project={project}')
  for command in commands:
    elements.append(command)
  return testCase.runner.invoke(cli, elements)

def insertSandboxData(testCase):
  # FIXME eventually this should probably pull in data from some sort of
  # FIXME external fixture file

  # create and initialize frotz database file
  db = ProjectDB()
  dbPath = os.path.join(testCase.slmhome, "projects", "frotz", "frotz.db")
  db.createDB(dbPath)
  db.initializeDBTables()

  # manually add data to frotz DB file
  subprojects = [
    Subproject(id=1, name="frotz-dim", desc="FROTZ with dim settings"),
    Subproject(id=2, name="frotz-shiny", desc="FROTZ with shiny settings"),
    Subproject(id=3, name="frotz-nuclear", desc="FROTZ with nuclear settings"),
  ]
  db.session.bulk_save_objects(subprojects)
  db.session.commit()

  # and close it
  db.closeDB()
