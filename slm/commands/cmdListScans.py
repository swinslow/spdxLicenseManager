# commands/cmdListScans.py
#
# Implementation of 'list-scans' command for spdxLicenseManager.
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

import sys
import click

from .helperContext import extractContext

def cmdListScans(ctx, subproject=None):
  slmhome, mainconfig, project, db = extractContext(ctx)

  if subproject:
    scans = db.getScansFiltered(subproject=subproject)
    click.echo(f"Scans for project {project}, subproject {subproject}:\n")
  else:
    scans = db.getScansAll()
    click.echo(f"Scans for project {project}:\n")

  # determine max column lengths for formatting
  col_id = len("ID")
  col_subp = len("Subproject")
  col_date = len("Date")
  col_desc = len("Description")
  for scan in scans:
    if scan.subproject:
      subpName = scan.subproject.name
    else:
      subpName = "NO NAME"
    len_id = len(str(scan._id))
    len_subp = len(str(scan.subproject.name))
    len_date = len(str(scan.scan_dt))
    len_desc = len(str(scan.desc))

    col_id = max(col_id, len_id)
    col_subp = max(col_subp, len_subp)
    col_date = max(col_date, len_date)
    col_desc = max(col_desc, len_desc)

  # add buffer spacing to all except rightmost column
  col_id += 2
  col_subp += 2
  col_date += 2

  # print column headers, with spacing for all except rightmost column
  click.echo(f'{_ch("ID", col_id)}{_ch("Subproject", col_subp)}{_ch("Date", col_date)}Description')
  click.echo(f'{_ch("==", col_id)}{_ch("==========", col_subp)}{_ch("====", col_date)}===========')

  # now, finally build and print the scan lines
  for scan in scans:
    if scan.subproject:
      subpName = scan.subproject.name
    else:
      subpName = "NO NAME"
    click.echo(f"{_ch(scan._id, col_id)}{_ch(subpName, col_subp)}{_ch(scan.scan_dt, col_date)}{scan.desc}")

# column string helper
def _ch(val, colsize):
  # add however many spaces are needed to make the column the right size
  s = str(val)
  spaces = colsize - len(s)
  return f"{s}{' ' * spaces}"
