# commands/cmdList.py
#
# Implementation of 'list' command for spdxLicenseManager.
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

def cmdList(ctx):
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  db = ctx.obj.get('PROJECTDB', None)
  project = ctx.obj.get('PROJECT', None)
  verbose = ctx.obj.get('VERBOSE', False)

  if project is not None:
    # list all subprojects for this project
    for sp in db.getSubprojectsAll():
      if verbose:
        click.echo(f"{project}/{sp.name}\t{sp.desc}")
      else:
        click.echo(f"{project}/{sp.name}")
  else:
    # list all projects
    for p in mainconfig.projects:
      if verbose:
        click.echo(f"{p.name}\t{p.desc}")
      else:
        click.echo(p.name)
