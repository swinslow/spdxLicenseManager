# commands/cmdEditLicense.py
#
# Implementation of 'edit-license' command for spdxLicenseManager.
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

import sys
import click

from .helperContext import extractContext
from ..projectdb import ProjectDBUpdateError

def cmdEditLicense(ctx, name, newName, newCat):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm that this license exists
  if db.getLicense(name=name) is None:
    # error, shouldn't call edit-license with license that doesn't exist yet
    sys.exit(f"License '{name}' does not exist in project {project}.\nDid you mean to call add-license instead?")

  # need to request at least one of the edit options
  if newName is None and newCat is None:
    sys.exit("For edit-license, need to specify at least one of --new-name or --new-cat")

  if name == newName:
    sys.exit(f"Cannot rename '{name}' to itself.")

  # change name if requested
  if newName is not None:
    try:
      db.changeLicenseName(name=name, newName=newName)
    except ProjectDBUpdateError as e:
      sys.exit(f"Cannot rename '{name}' license to '{newName}'; another license already has that name.")
    click.echo(f"Updated name of {name} to {newName}")

  # change category if requested
  if newCat is not None:
    try:
      db.changeLicenseCategory(name=name, newCat=newCat)
    except ProjectDBUpdateError as e:
      sys.exit(e)
    click.echo(f"Updated category of {name} to {newCat}")

  # clean up database
  db.closeDB()
