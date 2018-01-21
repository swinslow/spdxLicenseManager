# commands/cmdAddConversion.py
#
# Implementation of 'add-conversion' command for spdxLicenseManager.
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
from ..projectdb import ProjectDBInsertError

def cmdAddConversion(ctx, old_text, new_license):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm that this license exists
  if db.getLicense(name=new_license) is None:
    # error, shouldn't call add-conversion with license that doesn't exist yet
    sys.exit(f"License '{new_license}' does not exist yet.\nDid you mean to call add-license first?")

  # create conversion in database
  try:
    db.addConversion(old_text=old_text, new_license=new_license)
  except ProjectDBInsertError as e:
    sys.exit(e)

  # let the user know it worked
  click.echo(f"Created conversion: '{old_text}' => '{new_license}'")

  # clean up database
  db.closeDB()
