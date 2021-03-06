# commands/cmdListLicenses.py
#
# Implementation of 'list-licenses' command for spdxLicenseManager.
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
from ..projectdb import ProjectDBQueryError

def cmdListLicenses(ctx, by_category, in_category):
  slmhome, mainconfig, project, db = extractContext(ctx)

  if by_category and in_category:
    # can't do both
    sys.exit("Cannot use both --by-category and --in-category flags with the list-licenses command.")

  if by_category:
    # list all licenses, sorted by category order and then alphabetically
    last_cat = None
    for (cat, lic) in db.getLicensesAllByCategory():
      if cat != last_cat:
        # in new category; print cat name
        click.echo(f"{cat}:")
        last_cat = cat
      click.echo(f"  {lic}")

  elif in_category:
    # list all licenses in just this category, sorted alphabetically
    try:
      for lic in db.getLicensesInCategory(category=in_category):
        click.echo(f"{lic.name}")
    except ProjectDBQueryError as e:
      sys.exit(e)

  else:
    # list all licenses, sorted alphabetically
    for lic in db.getLicensesAll():
      click.echo(f"{lic.name}")
