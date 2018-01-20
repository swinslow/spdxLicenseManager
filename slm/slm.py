# slm.py
#
# Main entry point for spdxLicenseManager commands.
#
# Copyright (C) The Linux Foundation
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

from .commands.cmdInit import cmdInit
from .commands.cmdList import cmdList
from .commands.cmdCreate import cmdCreateProject, cmdCreateSubproject
from .commands.cmdAddCategory import cmdAddCategory
from .commands.cmdEditCategory import cmdEditCategory
from .commands.cmdListCategories import cmdListCategories
from .commands.cmdAddLicense import cmdAddLicense
from .commands.cmdListLicenses import cmdListLicenses
from .commands.cmdEditLicense import cmdEditLicense

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
def cliInit(ctx, newhome):
  return cmdInit(ctx, newhome)

######################
##### Project commands
######################

@cli.command('list', help="List projects or subprojects")
@click.pass_context
def cliList(ctx):
  return cmdList(ctx)

@cli.command('create-project', help="Create a new project")
@click.argument('name')
@click.option('--desc', default='NO DESCRIPTION', help='description for new project')
@click.pass_context
def cliCreateProject(ctx, name, desc):
  return cmdCreateProject(ctx, name, desc)

@cli.command('create-subproject', help="Create a new subproject")
@click.argument('name')
@click.option('--desc', help='description for new subproject')
@click.pass_context
def cliCreateSubproject(ctx, name, desc):
  return cmdCreateSubproject(ctx, name, desc)

#######################
##### Category commands
#######################

@cli.command('add-category', help="Add a new category of licenses")
@click.argument('name')
@click.option('--order', default=None, help='ordering of categories in reports')
@click.pass_context
def cliAddCategory(ctx, name, order):
  checkForContext(ctx)
  return cmdAddCategory(ctx, name, order)

@cli.command('edit-category', help="Edit a category of licenses")
@click.argument('name')
@click.option('--new-name', default=None, help='revised name for category')
@click.option('--sort-before', default=None, help='name of category that should come after this one in reports')
@click.pass_context
def cliEditCategory(ctx, name, new_name, sort_before):
  checkForContext(ctx)
  return cmdEditCategory(ctx, name, new_name, sort_before)

@cli.command('list-categories', help="List categories of licenses")
@click.pass_context
def cliListCategories(ctx):
  checkForContext(ctx)
  return cmdListCategories(ctx)

######################
##### License commands
######################

@cli.command('add-license', help="Add a new license")
@click.argument('name')
@click.argument('category')
@click.pass_context
def cliAddLicense(ctx, name, category):
  checkForContext(ctx)
  return cmdAddLicense(ctx, name, category)

@cli.command('list-licenses', help="List licenses")
@click.option('-c', '--by-category', is_flag=True, help='Sort by category')
@click.option('--in-category', default=None, 
  help='List licenses in just one category')
@click.pass_context
def cliListLicenses(ctx, by_category, in_category):
  checkForContext(ctx)
  return cmdListLicenses(ctx, by_category, in_category)

@cli.command('edit-license', help="Edit a license")
@click.argument('name')
@click.option('--new-name', default=None, help='revised name for license')
@click.option('--new-cat', default=None, help='name of category for license')
@click.pass_context
def cliEditLicense(ctx, name, new_name, new_cat):
  checkForContext(ctx)
  return cmdEditLicense(ctx, name, new_name, new_cat)
