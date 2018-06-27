# commands/cmdList.py
#
# Implementation of 'list' command for spdxLicenseManager.
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

import click
from tabulate import tabulate

from ..slmmanager import SLMManager

def aster(b):
  if b == True:
    return "*"
  else:
    return " "

def cmdStatus(ctx, year_month):
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  slmhome = ctx.obj.get('SLMHOME', None)
  manager = SLMManager(config=mainconfig, root=slmhome)

  click.echo(f"Month: {year_month}")
  click.echo("")

  # build status table
  headers = ["Project", "Subproject", "SPDX", "Scan", "JSON", "XLSX"]
  table = []
  for p in mainconfig.projects:
    pdb = manager.openProjectDB(p.name)
    subprojects = pdb.getSubprojectsAll()
    for sp in subprojects:
      isSPDX = aster(manager.isSPDXForMonth(pdb, p.name, sp.name, year_month))
      isScan = aster(manager.isScanForMonth(pdb, sp.name, year_month))
      isXLSX = aster(manager.isXLSXForMonth(p.name, sp.name, year_month))
      isJSON = aster(manager.isJSONForMonth(p.name, sp.name, year_month))
      sp_row = [p.name, sp.name, isSPDX, isScan, isXLSX, isJSON]
      table.append(sp_row)
    pdb.closeDB()

  # print status table with headers
  click.echo(tabulate(table, headers=headers))
