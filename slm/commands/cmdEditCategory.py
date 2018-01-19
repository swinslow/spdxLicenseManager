# commands/cmdEditCategory.py
#
# Implementation of 'edit-category' command for spdxLicenseManager.
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

import sys
import click

from .helperContext import extractContext
from ..projectdb import ProjectDBUpdateError

def cmdEditCategory(ctx, name, newName, sortBefore):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm that this category exists
  if db.getCategory(name=name) is None:
    # error, shouldn't call edit-category with category that doesn't exist yet
    sys.exit(f"Category '{name}' does not exist in project {project}.\nDid you mean to call add-category instead?")

  # need to request at least one of the edit options
  if newName is None and sortBefore is None:
    sys.exit("For edit-command, need to specify at least one of --new-name or --sort-before")

  if name == newName:
    sys.exit(f"Cannot rename '{name}' to itself.")
  if name == sortBefore:
    sys.exit(f"Cannot sort '{name}' before itself.")

  # change name if requested
  if newName is not None:
    try:
      db.changeCategoryName(name=name, newName=newName)
    except ProjectDBUpdateError as e:
      sys.exit(f"Cannot rename '{name}' category to '{newName}'; another category already has that name.")
    click.echo(f"Updated name of {name} to {newName}")

  # change ordering if requested
  if sortBefore is not None:
    try:
      db.changeCategoryOrder(name=name, sortBefore=sortBefore)
    except ProjectDBUpdateError as e:
      sys.exit(e)
    click.echo(f"Updated ordering of {name} to before {sortBefore}")

  # clean up database
  db.closeDB()