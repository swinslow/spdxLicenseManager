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
import sys
import click

from .__about__ import __version__

from .slmconfig import SLMConfig, BadSLMConfigError
from .projectdb import ProjectDB, ProjectDBConfigError

from .cmdinit import cmdinit
from .cmdlist import cmdlist
from .cmdcreate import cmdcreateProject, cmdcreateSubproject
from .cmdaddcategory import cmdaddCategory
from .cmdeditcategory import cmdeditCategory
from .cmdlistcategories import cmdlistCategories

VERSION_MESSAGE = f"spdxLicenseManager (slm) version {__version__}"

@click.group()
@click.version_option(message=VERSION_MESSAGE)
@click.option('--slmhome', default=None, envvar='SLM_HOME',
  help='path to spdxLicenseManager data directory')
@click.option('--project', default=None, envvar='SLM_PROJECT',
  help='project short name')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.pass_context
def cli(ctx, slmhome, project, verbose):
  ctx.obj = {}

  # parse any top-level options
  ctx.obj['SLMHOME'] = slmhome
  ctx.obj['PROJECT'] = project
  ctx.obj['VERBOSE'] = verbose

  # if slmhome is set, load config file and set on context
  # if slmhome is not set, just pass in an empty SLMConfig object
  mainconfig = SLMConfig()
  if slmhome is not None:
    try:
      mainconfigPath = os.path.join(os.path.abspath(slmhome), "slmconfig.json")
      with open(mainconfigPath, "r") as f:
        configData = f.read()
        mainconfig.loadConfig(configData)
    except BadSLMConfigError as e:
      sys.exit(str(e.message))
  ctx.obj['SLMCONFIG_DATA'] = mainconfig

  # if slmhome and project are set, load project database and set on context
  # if not, just pass in None
  if slmhome is None or project is None:
    db = None
  else:
    db = ProjectDB()
    projectDBRelativePath = mainconfig.getDBRelativePath(project)
    projectDBPath = os.path.join(
      os.path.abspath(slmhome), projectDBRelativePath
    )
    try:
      db.openDB(projectDBPath)
    except ProjectDBConfigError as e:
      sys.exit(str(e.message))
  ctx.obj['PROJECTDB'] = db

##### Helpers

def checkForContext(ctx):
  slmhome = ctx.obj.get('SLMHOME', None)
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  project = ctx.obj.get('PROJECT', None)
  db = ctx.obj.get('PROJECTDB', None)

  if slmhome is None:
    sys.exit("spdxLicenseManager data directory not specified.\nPlease specify with --slmhome or with SLM_HOME environment variable.")

  if mainconfig is None:
    sys.exit(f"Couldn't load main spdxLicenseManager configuration file from {slmhome}/slmconfig.json.")

  if project is None:
    sys.exit(f"No project specified.\nPlease specify a project with --project=PROJECT or the SLM_PROJECT environment variable.")

  if db is None:
    sys.exit(f"Couldn't load project database from {slmhome}/projects/{project}/{project}.db.")

##### Commands

@cli.command('init', help="Initialize a new SLM data directory")
@click.argument('newhome')
@click.pass_context
def cliinit(ctx, newhome):
  return cmdinit(ctx, newhome)

@cli.command('list', help="List projects or subprojects")
@click.pass_context
def clilist(ctx):
  return cmdlist(ctx)

@cli.command('create-project', help="Create a new project")
@click.argument('name')
@click.option('--desc', default='NO DESCRIPTION', help='description for new project')
@click.pass_context
def clicreateProject(ctx, name, desc):
  return cmdcreateProject(ctx, name, desc)

@cli.command('create-subproject', help="Create a new subproject")
@click.argument('name')
@click.option('--desc', help='description for new subproject')
@click.pass_context
def clicreateSubproject(ctx, name, desc):
  return cmdcreateSubproject(ctx, name, desc)

@cli.command('add-category', help="Add a new category of licenses")
@click.argument('name')
@click.option('--order', default=None, help='ordering of categories in reports')
@click.pass_context
def cliaddCategory(ctx, name, order):
  checkForContext(ctx)
  return cmdaddCategory(ctx, name, order)

@cli.command('edit-category', help="Edit a category of licenses")
@click.argument('name')
@click.option('--new-name', default=None, help='revised name for category')
@click.option('--sort-before', default=None, help='name of category that should come after this one in reports')
@click.pass_context
def cliaddCategory(ctx, name, new_name, sort_before):
  checkForContext(ctx)
  return cmdeditCategory(ctx, name, new_name, sort_before)

@cli.command('list-categories', help="List categories of licenses")
@click.pass_context
def clilistCategories(ctx):
  checkForContext(ctx)
  return cmdlistCategories(ctx)
