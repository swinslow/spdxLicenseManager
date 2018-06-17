# commands/cmdAddComponentLocation.py
#
# Implementation of 'add-component-location' command for spdxLicenseManager.
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

def cmdAddComponentLocation(ctx, component_name, location, absolute, scan_id):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # get ID for component
  component = db.getComponent(name=component_name, scan_id=scan_id)

  # create component-location in database
  try:
    db.addComponentLocation(component_id=component._id, path=location, absolute=absolute)
  except ProjectDBInsertError as e:
    sys.exit(e)

  # let the user know it worked
  click.echo(f"Added location to {component_name} for scan {scan_id}")

  # clean up database
  db.closeDB()
