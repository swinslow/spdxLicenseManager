# commands/cmdCreateReports.py
#
# Implementation of 'create-reports' command for spdxLicenseManager.
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

def cmdCreateReports(ctx, force=False):

  slmhome, mainconfig, project, db = extractContext(ctx)

  # cycle through all scans for this project
  numReports = 0
  scans = db.getScansAll()
  for scan in scans:

    # construct the scan's default path
    subproject_name = scan.subproject.name
    scan_dt_str = scan.scan_dt.strftime("%Y-%m")
    filename_pref = f"{subproject_name}-{scan_dt_str}"
    report_path_pref = os.path.join(slmhome, "projects", project, "subprojects",
      subproject_name, "reports", filename_pref)

    # analyze this scan
    analyzer = Analyzer(db=db)
    results = analyzer.runAnalysis(scan._id)

    # create xlsx report
    xlsxReporter = XlsxReporter(db=db, config={})
    xlsxReporter.setResults(results)
    xlsxReporter.generate()
    xlsxPath = report_path_pref + ".xlsx"
    try:
      xlsxReporter.save(path=xlsxPath, replace=force)
      numReports += 1
    except ReportFileError as e:
      if "File already exists" not in str(e):
        click.echo(f"Error creating XLSX report for scan {scan._id} at {xlsxPath}: {str(e)}")

    # create json report
    jsonReporter = JSONReporter(db=db, config={})
    # JSON reports must get results as a reformatted list
    listResults = analyzer.getResultsAsList()
    jsonReporter.setResults(listResults)
    jsonPath = report_path_pref + ".json"
    try:
      jsonReporter.save(path=jsonPath, replace=force)
      numReports += 1
    except ReportFileError as e:
      if "File already exists" not in str(e):
        click.echo(f"Error creating JSON report for scan {scan._id} at {jsonPath}: {str(e)}")

  # and confirm success
  if numReports == 1:
    click.echo(f"1 report successfully created")
  else:
    click.echo(f"{numReports} reports successfully created")
