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

def setUpSandbox(testCase, cli):
  # set up initial temp directory
  testCase.td = TempDirectory()

  # initialize the directory
  sandboxPath = os.path.join(testCase.td.path, "sandbox")
  testCase.runner.invoke(cli, ['init', sandboxPath])

  # set slmhome variable for test case
  testCase.slmhome = sandboxPath

def tearDownSandbox(testCase):
  testCase.td.cleanup()

def runcmd(testCase, cli, project, *commands):
  elements = [f'--slmhome={testCase.slmhome}']
  if project is not None:
    elements.append(f'--project={project}')
  for command in commands:
    elements.append(command)
  return testCase.runner.invoke(cli, elements)

def sandboxcmd(testCase, cli, *commands):
  elements = [f'--slmhome={testCase.slmhome}', '--project=frotz']
  for command in commands:
    elements.append(command)
  testCase.runner.invoke(cli, elements)

def runSandboxCommands(testCase, cli):
  # create some test projects
  # use invoke rather than sandboxcmd b/c these are not --project=frotz
  testCase.runner.invoke(cli, [f'--slmhome={testCase.slmhome}',
    'create-project', 'frotz', '--desc="The FROTZ Project"'])
  testCase.runner.invoke(cli, [f'--slmhome={testCase.slmhome}',
    'create-project', 'rezrov', '--desc="The REZROV Project"'])
  testCase.runner.invoke(cli, [f'--slmhome={testCase.slmhome}',
    'create-project', 'gnusto', '--desc="The GNUSTO Project"'])

  # and some test subprojects
  sandboxcmd(testCase, cli, 'create-subproject', 'frotz-dim',
    '--desc="FROTZ with dim settings"')
  sandboxcmd(testCase, cli, 'create-subproject', 'frotz-shiny',
    '--desc="FROTZ with shiny settings"')
  sandboxcmd(testCase, cli, 'create-subproject', 'frotz-nuclear',
    '--desc="FROTZ with nuclear settings"')

  # and some test categories
  sandboxcmd(testCase, cli, 'add-category', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-category', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-category', 'Attribution')

  # and some test licenses
  sandboxcmd(testCase, cli, 'add-license', 'Apache-2.0', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-license', 'CC-BY-4.0', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-license', 'GPL-2.0-only', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-license', 'GPL-2.0-or-later', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-license', 'BSD-2-Clause', 'Attribution')
  sandboxcmd(testCase, cli, 'add-license', 'MIT', 'Attribution')
