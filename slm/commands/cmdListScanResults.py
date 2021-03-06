# commands/cmdListScanResults.py
#
# Implementation of 'list-scan-results' command for spdxLicenseManager.
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

def cmdListScanResults(ctx, scan_id=None):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # check whether a scan ID was provided
  if scan_id is None:
    sys.exit(f'Usage: slm list-scan-results --scan_id SCAN_ID\n\nError: "scan_id" not provided.')

  # confirm that scan with this ID exists
  scan = db.getScan(_id=scan_id)
  if scan is None:
    sys.exit(f"Scan ID {scan_id} does not exist.")

  for file in db.getFiles(scan_id):
    click.echo(f"{file.path} => {file.license.name}")
