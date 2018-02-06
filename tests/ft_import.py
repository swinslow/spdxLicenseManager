# tests/ft_import.py
#
# Functional tests for spdxLicenseManager: import SPDX tag-value files.
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

import unittest
import click
from click.testing import CliRunner

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)

# paths to various SPDX test files
PATH_SIMPLE_SPDX = "tests/testfiles/simple.spdx"
PATH_SIMPLE_ALL_KNOWN_SPDX = "tests/testfiles/simpleAllKnown.spdx"
PATH_SIMPLE_TWO_UNKNOWN_SPDX = "tests/testfiles/simpleTwoUnknown.spdx"
PATH_SIMPLE_DUPLICATE_PATHS_SPDX = "tests/testfiles/simpleDuplicatePaths.spdx"
PATH_SIMPLE_DUPLICATES_AND_UNKNOWNS_SPDX = "tests/testfiles/simpleDuplicatesAndUnknowns.spdx"
PATH_BROKEN_READING_NO_COLON_SPDX = "tests/testfiles/brokenReadingNoColon.spdx"
PATH_BROKEN_READING_MULTILINE_TEXT_SPDX = "tests/testfiles/brokenReadingMultilineText.spdx"
PATH_BROKEN_PARSING_BAD_FILECHECKSUM_TYPE_SPDX = "tests/testfiles/brokenParsingBadFileChecksumType.spdx"
PATH_BROKEN_PARSING_BAD_FILECHECKSUM_FORMAT_SPDX = "tests/testfiles/brokenParsingBadFileChecksumFormat.spdx"
PATH_BROKEN_IMPORTING_NO_FILE_DATA_SPDX = "tests/testfiles/brokenImportingNoFileData.spdx"

class SPDXImportFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager tag-value importer FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_import_spdx_tag_value_file_and_get_results(self):
    # Edith has a very short SPDX file. She imports it as a new scan in
    # the frotz subproject frotz-dim
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_ALL_KNOWN_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It tells her that the scan was successfully added, and how to find it
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"Successfully imported 4 files from {PATH_SIMPLE_ALL_KNOWN_SPDX}\nScan ID is 3\n", result.output)

    # She now tries to print the scan results
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "list-scan-results", "--scan_id", "3")

    # They are displayed in a simple text format, alphabetically by file path
    self.assertEqual(0, result.exit_code)
    self.assertEqual(
f"""simple/dir1/subfile.txt => BSD-2-Clause
simple/file1.txt => BSD-2-Clause
simple/file2.txt => MIT
simple/file3.txt => BSD-2-Clause
""", result.output)

  def test_cannot_import_spdx_file_without_specifying_a_subproject(self):
    # Edith forgets to list a subproject when she tries to import an SPDX file
    result = runcmd(self, slm.cli, "frotz",
      "import-scan", PATH_SIMPLE_ALL_KNOWN_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f'Usage: slm --subproject SUBPROJECT import-scan SPDX_PATH [OPTIONS]\n\nError: Missing argument "subproject". Include "--subproject SUBPROJECT" before import-scan command, or set SLM_SUBPROJECT environment variable.\n',result.output)

  def test_cannot_import_spdx_file_that_does_not_exist(self):
    # Edith accidentally tries to import an SPDX file with an invalid path
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", "DOES_NOT_EXIST", "--scan_date", "2017-05-05",
      "--desc", "missing spdx file")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f'File not found: DOES_NOT_EXIST\n',result.output)

  def test_cannot_import_spdx_file_with_missing_colon(self):
    # Edith accidentally tries to import an SPDX file which has a line
    # with a tag, but no colon or value
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_BROKEN_READING_NO_COLON_SPDX,
      "--scan_date", "2017-05-05", "--desc", "invalid file missing colon")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertIn(f'Error reading {PATH_BROKEN_READING_NO_COLON_SPDX}: No colon found at line', result.output)

  def test_cannot_import_spdx_file_with_no_closing_text_field(self):
    # Edith accidentally tries to import an SPDX file which has a multiline
    # <text> value that never closes
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_BROKEN_READING_MULTILINE_TEXT_SPDX,
      "--scan_date", "2017-05-05", "--desc", "invalid file missing colon")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertIn(f'Error reading {PATH_BROKEN_READING_MULTILINE_TEXT_SPDX}: No closing </text> tag found', result.output)

  def test_cannot_import_spdx_file_with_unknown_filechecksum_type(self):
    # Edith accidentally tries to import an SPDX file which has a
    # FileChecksum tag with an invalid (unknown) type
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_BROKEN_PARSING_BAD_FILECHECKSUM_TYPE_SPDX,
      "--scan_date", "2017-05-05", "--desc", "invalid FileChecksum type")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Error parsing {PATH_BROKEN_PARSING_BAD_FILECHECKSUM_TYPE_SPDX}: Unknown FileChecksum type: 'INVALID' found for file simple/file3.txt\n", result.output)

  def test_cannot_import_spdx_file_with_bad_filechecksum_format(self):
    # Edith accidentally tries to import an SPDX file which has a
    # FileChecksum tag with an invalid format
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_BROKEN_PARSING_BAD_FILECHECKSUM_FORMAT_SPDX,
      "--scan_date", "2017-05-05", "--desc", "invalid FileChecksum format")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertIn(f"Error parsing {PATH_BROKEN_PARSING_BAD_FILECHECKSUM_FORMAT_SPDX}: Invalid FileChecksum format:", result.output)
    self.assertIn(f"found for file simple/file3.txt", result.output)

  def test_cannot_import_spdx_file_with_no_filedata(self):
    # Edith accidentally tries to import an SPDX file which has some tag-value
    # pairs but no filedata
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_BROKEN_IMPORTING_NO_FILE_DATA_SPDX,
      "--scan_date", "2017-05-05", "--desc", "no FileName tag-values")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Error parsing {PATH_BROKEN_IMPORTING_NO_FILE_DATA_SPDX}: No file data found\n", result.output)

  def test_conversions_are_correctly_applied_on_import(self):
    # Edith has a very short SPDX file, which requires some conversions (e.g.
    # "NOASSERTION" => "No license found"). She imports it as a new scan in
    # the frotz subproject frotz-dim
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")

    # It tells her that the scan was successfully added, and how to find it
    self.assertEqual(0, result.exit_code)
    self.assertEqual(f"Successfully imported 4 files from {PATH_SIMPLE_SPDX}\nScan ID is 3\n", result.output)

    # She now tries to print the scan results
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "list-scan-results", "--scan_id", "3")

    # They are displayed in a simple text format, alphabetically by file path
    self.assertEqual(0, result.exit_code)
    self.assertEqual(
f"""simple/dir1/subfile.txt => No license found
simple/file1.txt => No license found
simple/file2.txt => MIT
simple/file3.txt => No license found
""", result.output)

  def test_fails_and_lists_unknown_licenses_on_import(self):
    # Edith tries to import an SPDX file which has some unknown licenses with
    # no conversions in the database
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_TWO_UNKNOWN_SPDX,
      "--scan_date", "2017-05-05", "--desc", "unknown licenses")

    # It fails and explains which licenses / conversions need to be added
    self.assertEqual(1, result.exit_code)
    self.assertEqual(
f"""The following unknown licenses were detected:
=====
GFDL-1.3-only
NCSA
=====
For each, run 'slm add-license' or 'slm add-conversion' before importing.
""", result.output)

  def test_fails_and_lists_duplicate_paths_on_import(self):
    # Edith tries to import an SPDX file which has some duplicate paths
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_DUPLICATE_PATHS_SPDX,
      "--scan_date", "2017-05-05", "--desc", "duplicate paths")

    # It fails and explains which paths were duplicates
    self.assertEqual(1, result.exit_code)
    self.assertEqual(
f"""The following duplicate file paths were detected:
=====
simple/dir1/subfile.txt
simple/file3.txt
=====
All duplicates should be removed from the SPDX file before importing.
""", result.output)

  def test_prints_duplicates_not_unknowns_if_both_present(self):
    # Edith tries to import an SPDX file which has both (a) some duplicate
    # paths, and (b) some unknown licenses
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_DUPLICATES_AND_UNKNOWNS_SPDX,
      "--scan_date", "2017-05-05",
      "--desc", "duplicate paths and unknown licenses")

    # It fails and prints the duplicate paths, but not the unknown licenses
    self.assertEqual(1, result.exit_code)
    self.assertIn("The following duplicate file paths were detected", result.output)
    self.assertNotIn("The following unknown licenses were detected", result.output)

  def test_cannot_list_results_for_a_nonexistent_scan(self):
    # Edith accidentally tries to list the files and licenses for an
    # incorrect scan ID
    result = runcmd(self, slm.cli, "frotz",
      "list-scan-results", "--scan_id", "13")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f"Scan ID 13 does not exist.\n", result.output)

  def test_cannot_list_results_without_scan_id(self):
    # Edith accidentally tries to list files and licenses for a scan but
    # forgets to provide a scan ID
    result = runcmd(self, slm.cli, "frotz", "list-scan-results")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual(f'Usage: slm list-scan-results --scan_id SCAN_ID\n\nError: "scan_id" not provided.\n', result.output)

  def test_will_strip_path_prefixes_if_configured(self):
    # Edith configures the importer to strip out common path prefixes
    result = runcmd(self, slm.cli, "frotz", "set-config",
      "strip_path_prefixes", "yes")
    self.assertEqual(0, result.exit_code)

    # She imports a simple scan
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "import-scan", PATH_SIMPLE_ALL_KNOWN_SPDX, "--scan_date", "2017-05-05",
      "--desc", "frotz-dim initial scan")
    self.assertEqual(0, result.exit_code)

    # She then prints the scan results
    result = runcmd(self, slm.cli, "frotz", "--subproject", "frotz-dim",
      "list-scan-results", "--scan_id", "3")

    # They are displayed with common path prefixes stripped
    self.assertEqual(0, result.exit_code)
    self.assertEqual(
f"""/dir1/subfile.txt => BSD-2-Clause
/file1.txt => BSD-2-Clause
/file2.txt => MIT
/file3.txt => BSD-2-Clause
""", result.output)
