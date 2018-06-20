# commands/cmdEditSubproject.py
#
# Implementation of 'edit-subproject' command for spdxLicenseManager.
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

def cmdEditSubproject(ctx, subproject, spdx_search):
  slmhome, mainconfig, project, db = extractContext(ctx)

  if subproject is None:
    sys.exit("No subproject specified.\nPlease specify a subproject with --subproject=SUBPROJECT or the SLM_SUBPROJECT environment variable.")

  try:
    db.changeSubprojectSPDXSearch(name=subproject, spdx_search=spdx_search)
  except ProjectDBUpdateError as e:
    sys.exit(e)
  click.echo(f"Updated SPDX search string of {subproject} to {spdx_search}")

  # clean up database
  db.closeDB()
