# commands/cmdAddComponent.py
#
# Implementation of 'add-component' command for spdxLicenseManager.
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

def cmdAddComponent(ctx, name, scan_id, component_type):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # get ID for component type
  ct = db.getComponentType(name=component_type)

  # create component in database
  try:
    db.addComponent(name=name, scan_id=scan_id, component_type_id=ct._id)
  except ProjectDBInsertError as e:
    sys.exit(e)

  # let the user know it worked
  click.echo(f"Created component for scan {scan_id}: {name} ({component_type})")

  # clean up database
  db.closeDB()
