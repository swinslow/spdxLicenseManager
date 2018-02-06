# tests/helper_sandbox.py
#
# Helper for spdxLicenseManager: set up default sandbox for functional tests.
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
import shutil
from testfixtures import TempDirectory
from traceback import print_tb

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

  # and some test configuration values
  sandboxcmd(testCase, cli, 'set-config', 'strip_LicenseRef', 'yes')
  sandboxcmd(testCase, cli, 'set-config', 'vendor_dirs',
    'vendor;thirdparty;third-party')

  # and some test categories
  sandboxcmd(testCase, cli, 'add-category', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-category', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-category', 'Attribution')
  sandboxcmd(testCase, cli, 'add-category', 'No license found')

  # and some test licenses
  sandboxcmd(testCase, cli, 'add-license', 'Apache-2.0', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-license', 'CC-BY-4.0', 'Project Licenses')
  sandboxcmd(testCase, cli, 'add-license', 'GPL-2.0-only', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-license', 'GPL-2.0-or-later', 'Copyleft')
  sandboxcmd(testCase, cli, 'add-license', 'BSD-2-Clause', 'Attribution')
  sandboxcmd(testCase, cli, 'add-license', 'MIT', 'Attribution')
  sandboxcmd(testCase, cli, 'add-license', 'No license found', 'No license found')

  # and some test conversions
  sandboxcmd(testCase, cli, 'add-conversion', 'GPL-2.0+', 'GPL-2.0-or-later')
  sandboxcmd(testCase, cli, 'add-conversion', 'Expat', 'MIT')
  sandboxcmd(testCase, cli, 'add-conversion', 'NOASSERTION', 'No license found')
  sandboxcmd(testCase, cli, 'add-conversion', 'NONE', 'No license found')

  # and import a scan
  sandboxcmd(testCase, cli, "--subproject", "frotz-nuclear",
      "import-scan", "tests/testfiles/slm-2018-01-26.spdx",
      "--scan_date", "2018-01-26", "--desc", "frotz-nuclear initial scan")

def printResultDebug(result):
  tb = result.exc_info[2]
  print(f"exc_info = {result.exc_info}")
  print(f"exception = {result.exception}")
  print(f"exit_code = {result.exit_code}")
  print(f"output = {result.output}")
  print(f"output_bytes = {result.output_bytes}")
  print(f"runner = {result.runner}")
  print(f"=====TRACEBACK=====")
  print_tb(tb)
