# slm.py
#
# Main entry point for spdxLicenseManager commands.
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
from .commands.cmdSetConfig import cmdSetConfig
from .commands.cmdGetConfig import cmdGetConfig
from .commands.cmdListConfig import cmdListConfig
from .commands.cmdUnsetConfig import cmdUnsetConfig
from .commands.cmdGetConversion import cmdGetConversion
from .commands.cmdAddConversion import cmdAddConversion
from .commands.cmdEditConversion import cmdEditConversion
from .commands.cmdListConversions import cmdListConversions
from .commands.cmdImportScan import cmdImportScan
from .commands.cmdListScanResults import cmdListScanResults
from .commands.cmdListScans import cmdListScans
from .commands.cmdCreateReport import cmdCreateReport
from .commands.cmdRetrieveSPDX import cmdRetrieveSPDX
from .commands.cmdAddComponentType import cmdAddComponentType
from .commands.cmdListComponentTypes import cmdListComponentTypes
from .commands.cmdAddComponent import cmdAddComponent
from .commands.cmdListComponents import cmdListComponents
from .commands.cmdAddComponentLicense import cmdAddComponentLicense
from .commands.cmdAddComponentLocation import cmdAddComponentLocation

VERSION_MESSAGE = f"spdxLicenseManager (slm) version {__version__}"

@click.group()
@click.version_option(message=VERSION_MESSAGE)
@click.option('--slmhome', default=None, envvar='SLM_HOME',
  help='path to spdxLicenseManager data directory')
@click.option('--project', default=None, envvar='SLM_PROJECT',
  help='project short name')
@click.option('--subproject', default=None, envvar='SLM_SUBPROJECT',
  help='subproject short name')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.pass_context
def cli(ctx, slmhome, project, subproject, verbose):
  ctx.obj = {}

  # parse any top-level options
  ctx.obj['SLMHOME'] = slmhome
  ctx.obj['PROJECT'] = project
  ctx.obj['SUBPROJECT'] = subproject
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

####################################
##### Project configuration commands
####################################

@cli.command('set-config', help="Add or update configuration value")
@click.argument('key')
@click.argument('value')
@click.pass_context
def cliSetConfig(ctx, key, value):
  checkForContext(ctx)
  return cmdSetConfig(ctx, key, value)

@cli.command('get-config', help="Get configuration value")
@click.argument('key')
@click.pass_context
def cliGetConfig(ctx, key):
  checkForContext(ctx)
  return cmdGetConfig(ctx, key)

@cli.command('list-config', help="List all configuration values")
@click.pass_context
def cliListConfig(ctx):
  checkForContext(ctx)
  return cmdListConfig(ctx)

@cli.command('unset-config', help="Remove configuration value")
@click.argument('key')
@click.pass_context
def cliUnsetConfig(ctx, key):
  checkForContext(ctx)
  return cmdUnsetConfig(ctx, key)

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

#########################
##### Conversion commands
#########################

@cli.command('add-conversion', help="Add a new license name conversion")
@click.argument('old_text')
@click.argument('license_name')
@click.pass_context
def cliAddConversion(ctx, old_text, license_name):
  checkForContext(ctx)
  return cmdAddConversion(ctx, old_text, license_name)

@cli.command('get-conversion', help="Get a license name conversion")
@click.argument('old_text')
@click.pass_context
def cliGetConversion(ctx, old_text):
  checkForContext(ctx)
  return cmdGetConversion(ctx, old_text)

@cli.command('edit-conversion', help="Edit an existing license name conversion")
@click.argument('old_text')
@click.argument('license_name')
@click.pass_context
def cliEditConversion(ctx, old_text, license_name):
  checkForContext(ctx)
  return cmdEditConversion(ctx, old_text, license_name)

@cli.command('list-conversions', help="List conversions")
@click.pass_context
def cliListConversions(ctx):
  checkForContext(ctx)
  return cmdListConversions(ctx)

###################
##### Scan commands
###################

@cli.command('import-scan', help="Import an SPDX tag-value file as a new scan")
@click.argument('spdx_path')
@click.option('--scan_date', default=None, help='Scan date')
@click.option('--desc', default=None, help='Scan description')
@click.pass_context
def cliImportScan(ctx, spdx_path, scan_date, desc):
  checkForContext(ctx)
  subproject = ctx.obj['SUBPROJECT']
  return cmdImportScan(ctx, subproject, spdx_path, scan_date, desc)

@cli.command('list-scan-results', help="List all files and licenses in a scan")
@click.option('--scan_id', default=None, help='Scan ID')
@click.pass_context
def cliListScanResults(ctx, scan_id):
  checkForContext(ctx)
  return cmdListScanResults(ctx, scan_id)

@cli.command('list-scans', help="List scans")
@click.pass_context
def cliListScans(ctx):
  checkForContext(ctx)
  subproject = ctx.obj['SUBPROJECT']
  return cmdListScans(ctx, subproject=subproject)

#####################
##### Report commands
#####################

@cli.command('create-report', help="Create report from scan in database")
@click.option('--scan_id', default=None, help='Scan ID')
@click.option('--report_path', default=None, help='Output file path')
@click.option('--report_format', default=None, help='Report format')
@click.option('--no_summary', is_flag=True, help='Omit summary report')
@click.option('-f', '--force', is_flag=True, help='Force overwrite of existing output file')
@click.pass_context
def cliCreateReport(ctx, scan_id, report_path, report_format, no_summary, force):
  checkForContext(ctx)
  subproject = ctx.obj['SUBPROJECT']
  return cmdCreateReport(ctx, subproject, scan_id, report_path,
    report_format, no_summary, force)

#############################
##### SPDX retrieval commands
#############################

@cli.command('retrieve-spdx', help="Retrieve SPDX files for a given month")
@click.option('--month', default=None, help='Month in format YYYY-MM')
@click.pass_context
def cliRetrieveSPDX(ctx, month):
  checkForContext(ctx)
  return cmdRetrieveSPDX(ctx, month)

#############################
##### Component type commands
#############################

@cli.command('add-component-type', help="Add a new component type")
@click.argument('name')
@click.pass_context
def cliAddComponentType(ctx, name):
  checkForContext(ctx)
  return cmdAddComponentType(ctx, name)

@cli.command('list-component-types', help="List component types")
@click.pass_context
def cliListComponentTypes(ctx):
  checkForContext(ctx)
  return cmdListComponentTypes(ctx)

########################
##### Component commands
########################

@cli.command('add-component', help="Add a new component")
@click.argument('name')
@click.option('--scan_id', required=True, help='Scan ID')
@click.option('--component_type', required=True, help="Component type")
@click.pass_context
def cliAddComponent(ctx, name, scan_id, component_type):
  checkForContext(ctx)
  return cmdAddComponent(ctx, name, scan_id, component_type)

@cli.command('list-components', help="List components")
@click.option('--scan_id', required=True, help='Scan ID')
@click.pass_context
def cliListComponents(ctx, scan_id):
  checkForContext(ctx)
  return cmdListComponents(ctx, scan_id)

@cli.command('add-component-license', help="Add a license to an existing component")
@click.argument('component')
@click.argument('license')
@click.option('--scan_id', required=True, help='Scan ID')
@click.pass_context
def cliAddComponentLicense(ctx, component, license, scan_id):
  checkForContext(ctx)
  return cmdAddComponentLicense(ctx, component_name=component, license_name=license, scan_id=scan_id)

@cli.command('add-component-location', help="Add a location to an existing component")
@click.argument('component')
@click.argument('location')
@click.option('--scan_id', required=True, help='Scan ID')
@click.option('--absolute', is_flag=True, default=False, help='Location is absolute path')
@click.pass_context
def cliAddComponentLocation(ctx, component, location, scan_id, absolute):
  checkForContext(ctx)
  return cmdAddComponentLocation(ctx, component_name=component, location=location, scan_id=scan_id, absolute=absolute)
