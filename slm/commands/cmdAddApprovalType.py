# commands/cmdAddApprovalType.py
#
# Implementation of 'add-approval-type' command for spdxLicenseManager.
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

def cmdAddApprovalType(ctx, name):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # confirm approval type doesn't already exist for this project
  if db.getApprovalType(name=name) is not None:
    # error, shouldn't call add-approval-type with existing name
    sys.exit(f"Approval type '{name}' already exists for project {project}.")

  # create approval type in database
  try:
    db.addApprovalType(name=name)
  except ProjectDBInsertError as e:
    sys.exit(e)

  # let the user know it worked
  click.echo(f"Created approval type: {name}")

  # clean up database
  db.closeDB()
