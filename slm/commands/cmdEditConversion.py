# commands/cmdEditConversion.py
#
# Implementation of 'edit-conversion' command for spdxLicenseManager.
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
from ..projectdb import ProjectDBUpdateError

def cmdEditConversion(ctx, old_text, new_license):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm that this conversion exists
  if db.getConversion(old_text=old_text) is None:
    # error, shouldn't call edit-conversion with conversion that doesn't exist
    sys.exit(f"Conversion '{old_text}' does not exist in project {project}.\nDid you mean to call add-conversion instead?")

  # confirm that this license exists
  if db.getLicense(name=new_license) is None:
    # error, shouldn't call edit-conversion with license that doesn't exist
    sys.exit(f"License '{new_license}' does not exist yet.\nDid you mean to call add-license first?")

  try:
    db.changeConversion(old_text=old_text, new_license=new_license)
  except ProjectDBUpdateError as e:
    sys.exit(e)
  click.echo(f"Updated license for conversion of {old_text} to {new_license}")

  # clean up database
  db.closeDB()
