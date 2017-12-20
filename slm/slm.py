# slm.py
#
# Main entry point for spdxLicenseManager commands.
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
import click

from .__about__ import __version__

from .slmconfig import SLMConfig, BadSLMConfigError
from .projectconfig import ProjectConfig, BadProjectConfigError

from .cmdlist import cmdlist
from .cmdcreate import cmdcreateProject, cmdcreateSubproject

VERSION_MESSAGE = f"spdxLicenseManager (slm) version {__version__}"

@click.group()
@click.version_option(message=VERSION_MESSAGE)
@click.option('--slmhome', default=None, envvar='SLM_HOME',
  help='path to spdxLicenseManager data directory')
@click.option('--project', default=None, envvar='SLM_PROJECT',
  help='project short name')
@click.pass_context
def cli(ctx, slmhome, project):
  ctx.obj = {}

  # parse any top-level options
  ctx.obj['SLMHOME'] = slmhome
  ctx.obj['PROJECT'] = project

  # if slmhome is set, load config file and set on context
  # if slmhome is not set, just pass in an empty SLMConfig object
  mainconfig = SLMConfig()
  if slmhome is not None:
    try:
      mainconfigPath = os.path.join(os.path.abspath(slmhome), "slmconfig.json")
      with open(mainconfigPath, "r") as f:
        configData = f.read()
        mainconfig.loadConfig(configData)
    except BadSLMConfigError:
      sys.exit(f"Error parsing configuration data from {mainconfigPath}")
  ctx.obj['SLMCONFIG_DATA'] = mainconfig

  # if slmhome and project are set, load project config file and set on context
  # if not, just pass in an empty ProjectConfig object
  prjconfig = ProjectConfig()
  if slmhome is not None and project is not None:
    try:
      prjfilename = project + ".config.json"
      prjconfigPath = os.path.join(
        os.path.abspath(slmhome), "projects", project, prjfilename
      )
      with open(prjconfigPath, "r") as f:
        prjconfigData = f.read()
        prjconfig.loadConfig(prjconfigData)
    except BadProjectConfigError:
      sys.exit(f"Error parsing project configuration data from {prjconfigPath}")
  ctx.obj['PRJCONFIG_DATA'] = prjconfig

@cli.command('list')
@click.pass_context
def clilist(ctx):
  return cmdlist(ctx)

@cli.command('create-project')
@click.argument('name')
@click.option('--desc', help='description for new project')
@click.pass_context
def clicreateProject(ctx, name, desc):
  return cmdcreateProject(ctx, name, desc)

@cli.command('create-subproject')
@click.pass_context
def clicreateSubproject(ctx):
  return cmdcreateSubproject(ctx)
