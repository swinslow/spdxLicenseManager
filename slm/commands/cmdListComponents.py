# commands/cmdListComponents.py
#
# Implementation of 'list-components' command for spdxLicenseManager.
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

import click

from .helperContext import extractContext

def cmdListComponents(ctx, scan_id):
  slmhome, mainconfig, project, db = extractContext(ctx)
  verbose = ctx.obj.get('VERBOSE', False)

  for component in db.getComponentsAllForScan(scan_id=scan_id):
    if verbose:
      click.echo(f"{component.name}:")

      # get licenses string
      lics = db.getComponentLicenses(component_id=component._id)
      lics_names = [lic.name for lic in lics]
      lics_string = ', '.join(lics_names)

      click.echo(f"  licenses: {lics_string}")
      click.echo(f"  type: {component.component_type.name}")

      # also show file locations
      click.echo(f"  locations:")
      locs = db.getComponentLocations(component_id=component._id)
      for loc in locs:
        if not loc.absolute:
          click.echo(f"    *{loc.path}*")
        else:
          click.echo(f"    {loc.path}")
    else:
      click.echo(f"{component.name}")
