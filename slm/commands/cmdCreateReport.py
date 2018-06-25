# commands/cmdCreateReport.py
#
# Implementation of 'create-report' command for spdxLicenseManager.
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

import os
import sys
import click

from .helperContext import extractContext
from ..reports.analysis import Analyzer
from ..reports.common import ReportFileError
from ..reports.json import JSONReporter
from ..reports.xlsx import XlsxReporter

def cmdCreateReport(ctx, subproject, scan_id=None, report_path=None,
  report_format='xlsx', no_summary=False, force=False):

  slmhome, mainconfig, project, db = extractContext(ctx)

  # check whether a scan ID was provided
  if scan_id is None:
    sys.exit(f'Usage: slm create-report --scan_id SCAN_ID --report_path PATH [OPTIONS]\n\nError: "scan_id" not provided.')

  # confirm that scan with this ID exists
  scan = db.getScan(_id=scan_id)
  if scan is None:
    sys.exit(f"Scan ID {scan_id} does not exist.")

  # if no report_path was provided, construct the scan's default path
  if report_path is None:
    subproject_name = scan.subproject.name
    scan_dt_str = scan.scan_dt.strftime("%Y-%m-%d")
    filename = f"{subproject_name}-{scan_dt_str}.{report_format}"
    report_path = os.path.join(slmhome, "projects", project, "subprojects",
      subproject_name, "reports", filename)

  # check for config flags
  kwConfig = {}
  if no_summary:
    kwConfig['report-include-summary'] = 'no'

  # analyze this scan
  analyzer = Analyzer(db=db)
  results = analyzer.runAnalysis(scan_id)

  reporter = None
  if report_format == 'xlsx':
    reporter = XlsxReporter(db=db, config=kwConfig)
    reporter.setResults(results)
    reporter.generate()
  elif report_format == 'json':
    reporter = JSONReporter(db=db, config=kwConfig)
    # JSON reports must get results as a reformatted list
    listResults = analyzer.getResultsAsList()
    reporter.setResults(listResults)
  else:
    sys.exit(f"Unknown report format: {report_format}")

  try:
    reporter.save(path=report_path, replace=force)
  except ReportFileError as e:
    if "File already exists" in str(e):
      sys.exit(f"File already exists at {report_path} (use -f to force overwrite)")

  # and confirm success
  click.echo(f"Report successfully created at {report_path}.")
