# commands/cmdSetConfig.py
#
# Implementation of 'set-config' command for spdxLicenseManager.
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
from ..projectdb import ProjectDBInsertError, ProjectDBUpdateError

def cmdSetConfig(ctx, key, value):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # add or update config value in database
  try:
    db.setConfigValue(key=key, value=value)
  except ProjectDBUpdateError as e:
    sys.exit(e)
  except ProjectDBInsertError as e:
    sys.exit(e)

  # let the user know it worked
  click.echo(f"Configuration value set for '{key}'.")

  # clean up database
  db.closeDB()
