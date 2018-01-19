# commands/cmdListCategories.py
#
# Implementation of 'list-categories' command for spdxLicenseManager.
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

import click

from .helperContext import extractContext

def cmdListCategories(ctx):
  slmhome, mainconfig, project, db = extractContext(ctx)

  for cat in db.getCategoriesAll():
    click.echo(f"{cat.name}")
