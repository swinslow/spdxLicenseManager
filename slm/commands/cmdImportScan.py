# commands/cmdImportScan.py
#
# Implementation of 'import-scan' command for spdxLicenseManager.
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

from ..tvReader import TVReader
from ..tvParser import TVParser
from ..tvImporter import TVImporter

def cmdImportScan(ctx, subproject, spdx_path, scan_dt, desc):
  slmhome, mainconfig, project, db = extractContext(ctx)

  if subproject is None:
    sys.exit(f'Usage: slm --subproject SUBPROJECT import-scan SPDX_PATH [OPTIONS]\n\nError: Missing argument "subproject". Include "--subproject SUBPROJECT" before import-scan command, or set SLM_SUBPROJECT environment variable.')

  # first, check and validate that the SPDX tag-value doc is good to go
  try:
    with open(spdx_path, 'r') as f:
      # read in the tag-value pairs line-by-line
      reader = TVReader()
      for line in f:
        reader.readNextLine(line)
      tvList = reader.finalize()
      # check for errors
      if reader.isError():
        sys.exit(f"Error reading {spdx_path}: {reader.errorMessage}")

      # parse the tag-value pairs
      parser = TVParser()
      for tag, value in tvList:
        parser.parseNextPair(tag, value)
      fdList = parser.finalize()
      # check for errors
      if parser.isError():
        sys.exit(f"Error parsing {spdx_path}: {parser.errorMessage}")
      # empty list means no file data found
      if fdList == []:
        sys.exit(f"Error parsing {spdx_path}: No file data found")

      # check the parsed file data
      importer = TVImporter()
      retval = importer.checkFileDataList(fdList=fdList, db=db)
      if not retval:
        _handleImporterFailure(importer=importer)

      # create new scan and get ID
      scan_id = db.addScan(subproject=subproject, scan_dt_str=scan_dt,
        desc=desc)

      # import the validated file data
      importer.importFileDataList(fdList=fdList, db=db, scan_id=scan_id)

      # and report on how many files were imported
      count = importer.getImportedCount()
      click.echo(f"Successfully imported {count} files from {spdx_path}")
      click.echo(f"Scan ID is {scan_id}")

  except FileNotFoundError as e:
    sys.exit(f"File not found: {spdx_path}")

  # clean up database
  db.closeDB()

def _handleImporterFailure(importer):
  # failed because of unknown licenses?
  if importer.licensesUnknown != []:
    exitMessage = "The following unknown licenses were detected:\n=====\n"
    for lic in importer.licensesUnknown:
      exitMessage += f"{lic}\n"
    exitMessage += "=====\nFor each, run 'slm add-license' or 'slm add-conversion' before importing."
    sys.exit(exitMessage)

  # failed because of duplicate paths?
  if importer.pathDuplicates != []:
    exitMessage = "The following duplicate file paths were detected:\n=====\n"
    for path in importer.pathDuplicates:
      exitMessage += f"{path}\n"
    exitMessage += "=====\nAll duplicates should be removed from the SPDX file before importing."
    sys.exit(exitMessage)
