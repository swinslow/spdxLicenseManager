# tests/unit_retriever.py
#
# Unit test for spdxLicenseManager: retrieving SPDX files.
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
import unittest
from unittest import mock

from slm.retriever import (Retriever, RetrieverConfigError,
  RetrieverNotReadyError)
from slm.datatypes import Subproject

##### helper for testing _getFiles and prepareFiles
TFILES = ['fileone.spdx', 'filetwo', 'hello.sC.blah2018-03-17.blah.spdx']
TDIRS  = ['dirone', 'dirtwo', 'dirthree']
TALL   = TFILES + TDIRS

def side_effect_isfile(path):
  return path in TFILES

##### helper for testing createResults
MOVEFILES = [
  'junk.hello.junk.2018-03-12.spdx',
  'junk.hello.junk.2018-03.spdx',
  'junk.goodbye.junk.2018-03-20.spdx',
  'junk.goodbye.junk.2018-03-17.spdx',
  'junk.bonjour.junk.2018-03-01.spdx',
]
MOVE_SUBPROJECTS = [
  ('hello', 1, 'hello'),
  ('goodbye', 2, 'goodbye'),
  ('bonjourProject', 3, 'bonjour'),
  ('holaPrj', 4, 'hola'),
]


class RetrieverTestSuite(unittest.TestCase):
  """spdxLicenseManager SPDX retrieval unit test suite."""

  def setUp(self):
    # create retriever object
    self.retriever = Retriever()

  def tearDown(self):
    pass

  ##### Test cases below

  def test_new_retriever_is_in_expected_reset_state(self):
    self.assertEqual(self.retriever.subprojects, {})
    self.assertEqual(self.retriever.datestr, "")
    self.assertEqual(self.retriever.search_dir, "")
    self.assertEqual(self.retriever.project_dir, "")
    self.assertEqual(self.retriever.filesPrepared, False)
    self.assertEqual(self.retriever.results, {})

  ##### Getter and setter tests

  def test_can_set_datestr(self):
    self.retriever.setDatestr("2018-06")
    self.assertEqual("2018-06", self.retriever.datestr)

  def test_can_clear_datestr(self):
    self.retriever.setDatestr("")
    self.assertEqual("", self.retriever.datestr)

  def test_cannot_set_datestr_to_invalid_values(self):
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("blah")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018 06")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018-06-09")
    self.assertEqual("", self.retriever.datestr)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setDatestr("2018-30")
    self.assertEqual("", self.retriever.datestr)

  def test_can_add_subproject_data(self):
    self.retriever.addSubproject(name="subA", spdx_search="subA", _id=1)
    self.retriever.addSubproject(name="subC", spdx_search="sC", _id=3)
    self.retriever.addSubproject(name="subX", spdx_search="subX", _id=2)
    name, _id, files = self.retriever.subprojects.get("sC")
    self.assertEqual(3, _id)
    self.assertEqual([], files)

  def test_cannot_add_subproject_ids_or_spdx_search_with_invalid_types(self):
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search="", _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search=None, _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search=1, _id=1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search="hi", _id=0)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search="hi", _id=-1)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search="hi", _id=None)
    self.assertEqual({}, self.retriever.subprojects)
    with self.assertRaises(RetrieverConfigError):
      self.retriever.addSubproject(name='test', spdx_search="hi", _id="blah")
    self.assertEqual({}, self.retriever.subprojects)

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  def test_can_set_directories_to_existing_directories(self, mock_isdir):
    downloadsDir = "/tmp/fake/Downloads/directory"
    self.retriever.setSearchDir(downloadsDir)
    self.assertEqual(downloadsDir, self.retriever.search_dir)
    projectDir = "/tmp/fake/SLM/fakeproject"
    self.retriever.setProjectDir(projectDir)
    self.assertEqual(projectDir, self.retriever.project_dir)

  @mock.patch("slm.retriever.os.path.isdir", return_value=False)
  def test_cannot_set_directories_to_nonexistent_directories(self, mock_isdir):
    downloadsDir = "/tmp/fake/invalid/directory"
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setSearchDir(downloadsDir)
    self.assertEqual("", self.retriever.search_dir)
    projectDir = "/tmp/fake/invalid/non-project/directory"
    with self.assertRaises(RetrieverConfigError):
      self.retriever.setSearchDir(projectDir)
    self.assertEqual("", self.retriever.project_dir)

  ##### SPDX retrieval filename checker tests

  def test_proper_filenames_match(self):
    spdx_search = "hello"
    datestr = "2018-03"
    self.assertTrue(self.retriever._testFilename(filename="hello-2018-03-08.spdx", spdx_search=spdx_search, datestr=datestr))
    self.assertTrue(self.retriever._testFilename(filename="hello-other_stuff_2018-03-08-blah-whatever.spdx", spdx_search=spdx_search, datestr=datestr))
    self.assertTrue(self.retriever._testFilename(filename="datefirst-2018-03-08-blah-hello-ok.spdx", spdx_search=spdx_search, datestr=datestr))
    self.assertTrue(self.retriever._testFilename(filename="hellohello-2018-03-08.spdx", spdx_search=spdx_search, datestr=datestr))
    self.assertTrue(self.retriever._testFilename(filename="somethinghelloblah-2018-03-08.spdx", spdx_search=spdx_search, datestr=datestr))

  def test_improper_filenames_do_not_match(self):
    spdx_search = "hello"
    datestr = "2018-03"
    # no subproject search string or date
    self.assertFalse(self.retriever._testFilename(filename="blah.spdx", spdx_search=spdx_search, datestr=datestr))
    # no date
    self.assertFalse(self.retriever._testFilename(filename="hello.spdx", spdx_search=spdx_search, datestr=datestr))
    # no day
    self.assertFalse(self.retriever._testFilename(filename="hello-2018-03.spdx", spdx_search=spdx_search, datestr=datestr))
    # no hyphen between year and month
    self.assertFalse(self.retriever._testFilename(filename="hello-201803.spdx", spdx_search=spdx_search, datestr=datestr))
    # no hyphen between month and day
    self.assertFalse(self.retriever._testFilename(filename="hello-2018-0320.spdx", spdx_search=spdx_search, datestr=datestr))
    # no subproject search string
    self.assertFalse(self.retriever._testFilename(filename="2018-03-20.spdx", spdx_search=spdx_search, datestr=datestr))
    # invalid day
    self.assertFalse(self.retriever._testFilename(filename="hello-2018-03-40.spdx", spdx_search=spdx_search, datestr=datestr))
    # no .spdx extension
    self.assertFalse(self.retriever._testFilename(filename="hello-2018-03-08", spdx_search=spdx_search, datestr=datestr))

  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_can_get_files_from_search_directory(self, mock_listdir, mock_isfile):
    files = self.retriever._getFiles(search_dir="/tmp/fake/whatever")
    self.assertEqual(TFILES, files)

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_prepare_fails_if_subprojects_not_set(self, mock_listdir, mock_isfile, mock_isdir):
    self.retriever.setSearchDir('/tmp/fake/whatever')
    self.retriever.setDatestr(datestr='2018-03')
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.prepareFiles()

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_prepare_fails_if_datestr_not_set(self, mock_listdir, mock_isfile, mock_isdir):
    self.retriever.setSearchDir('/tmp/fake/whatever')
    self.retriever.addSubproject(name='subC', spdx_search='sC', _id=1)
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.prepareFiles()

  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_prepare_fails_if_search_dir_not_set(self, mock_listdir, mock_isfile):
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.addSubproject(name='subC', spdx_search='sC', _id=1)
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.prepareFiles()

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_cannot_prepare_files_twice(self, mock_listdir, mock_isfile, mock_isdir):
    self.retriever.setSearchDir('/tmp/fake/whatever')
    self.retriever.addSubproject(name='subC', spdx_search='sC', _id=1)
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.prepareFiles()
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.prepareFiles()

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  @mock.patch("slm.retriever.Retriever._testFilename")
  def test_prepare_calls_tester_for_each_file_in_search_directory(self, mock_testfilename, mock_listdir, mock_isfile, mock_isdir):
    self.retriever.setSearchDir('/tmp/fake/whatever')
    self.retriever.addSubproject(name='subC', spdx_search='sC', _id=1)
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.prepareFiles()
    expected = [
      mock.call('/tmp/fake/whatever/fileone.spdx', 'sC', '2018-03'),
      mock.call('/tmp/fake/whatever/filetwo', 'sC', '2018-03'),
      mock.call('/tmp/fake/whatever/hello.sC.blah2018-03-17.blah.spdx', 'sC', '2018-03'),
    ]
    self.assertEqual(expected, mock_testfilename.call_args_list)

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", side_effect=side_effect_isfile)
  @mock.patch("slm.retriever.os.listdir", return_value=TALL)
  def test_prepare_adds_matches_to_subproject(self, mock_listdir, mock_isfile, mock_isdir):
    self.retriever.setSearchDir('/tmp/fake/whatever')
    self.retriever.addSubproject(name='subC', spdx_search='sC', _id=1)
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.prepareFiles()
    self.assertTrue(self.retriever.filesPrepared)
    self.assertEqual(
      {'sC': ('subC', 1, ['/tmp/fake/whatever/hello.sC.blah2018-03-17.blah.spdx'])},
      self.retriever.subprojects
    )

  def test_create_results_fails_if_files_not_prepared(self):
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.createResults()

  def test_create_results_fails_if_results_are_not_empty(self):
    self.retriever.results = {'junk': 17}
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.createResults()

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", return_value=True)
  @mock.patch("slm.retriever.os.listdir", return_value=MOVEFILES)
  def test_create_results_fails_if_project_dir_not_set(self, mock_listdir, mock_isfile, mock_isdir):
    for name, _id, spdx_search in MOVE_SUBPROJECTS:
      self.retriever.addSubproject(name=name, _id=_id, spdx_search=spdx_search)
    self.retriever.setSearchDir('/tmp/fake/src')
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.prepareFiles()
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.createResults()

  @mock.patch("slm.retriever.os.path.isdir", return_value=True)
  @mock.patch("slm.retriever.os.path.isfile", return_value=True)
  @mock.patch("slm.retriever.os.listdir", return_value=MOVEFILES)
  def test_can_create_results_actions(self, mock_listdir, mock_isfile, mock_isdir):
    for name, _id, spdx_search in MOVE_SUBPROJECTS:
      self.retriever.addSubproject(name, _id=_id, spdx_search=spdx_search)
    self.retriever.setSearchDir('/tmp/fake/src')
    self.retriever.setProjectDir('/tmp/fake/dst')
    self.retriever.setDatestr(datestr='2018-03')
    self.retriever.prepareFiles()
    self.retriever.createResults()

    # check successes
    success = self.retriever.results.get('success')
    self.assertEqual((1, 'hello', '/tmp/fake/src/junk.hello.junk.2018-03-12.spdx', '/tmp/fake/dst/hello/spdx/hello-2018-03-12.spdx'), success[0])
    self.assertEqual((3, 'bonjourProject', '/tmp/fake/src/junk.bonjour.junk.2018-03-01.spdx', '/tmp/fake/dst/bonjourProject/spdx/bonjourProject-2018-03-01.spdx'), success[1])

    # check errors
    error = self.retriever.results.get('error')
    self.assertEqual((2, 'goodbye', 'Multiple valid matches found for project goodbye (with string "goodbye"):\n  /tmp/fake/src/junk.goodbye.junk.2018-03-17.spdx\n  /tmp/fake/src/junk.goodbye.junk.2018-03-20.spdx'), error[0])
    self.assertEqual((4, 'holaPrj', 'No matches found for project holaPrj (with string "hola")'), error[1])

  def test_can_get_dst_filename_from_helper(self):
    srcPath = "/tmp/whatever/junk.hello.junk.2018-03-12-morejunk.spdx"
    spdx_search = "hello"
    datestr = "2018-03"
    subproject_name = "helloPrj"
    dstFilename = self.retriever._makeDstFilename(srcPath=srcPath, spdx_search=spdx_search, datestr=datestr, subproject_name=subproject_name)
    self.assertEqual("helloPrj-2018-03-12.spdx", dstFilename)

  def test_dst_filename_helper_fails_if_invalid_date_in_string(self):
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever._makeDstFilename(srcPath="2018-03.spdx", spdx_search='a',
        datestr="2018-03", subproject_name='b')
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever._makeDstFilename(srcPath="2018-03-.spdx", spdx_search='a',
        datestr="2018-03", subproject_name='b')
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever._makeDstFilename(srcPath="2018-03-40.spdx",
        spdx_search='a', datestr="2018-03", subproject_name='b')

  @mock.patch("slm.retriever.shutil.move")
  def test_can_move_files(self, mock_move):
    self.retriever.results["success"] = [
      (1, 'hello', '/tmp/fake/src/junk.hello.junk.2018-03-12.spdx', '/tmp/fake/dst/hello/spdx/hello-2018-03-12.spdx')
    ]
    self.retriever.results["error"] = []
    self.retriever.moveFiles()
    mock_move.assert_called_with('/tmp/fake/src/junk.hello.junk.2018-03-12.spdx', '/tmp/fake/dst/hello/spdx/hello-2018-03-12.spdx')

  @mock.patch("slm.retriever.shutil.move")
  def test_cannot_move_files_before_results_are_set(self, mock_move):
    with self.assertRaises(RetrieverNotReadyError):
      self.retriever.moveFiles()

  @mock.patch("slm.retriever.os.path.isfile", return_value=True)
  @mock.patch("slm.retriever.shutil.move")
  def test_cannot_move_files_if_already_present_in_dst(self, mock_move, mock_isfile):
    self.retriever.results["success"] = [
      (1, 'hello', '/tmp/fake/src/junk.hello.junk.2018-03-12.spdx', '/tmp/fake/dst/hello/spdx/hello-2018-03-12.spdx')
    ]
    self.retriever.results["error"] = []
    self.retriever.moveFiles()
    # not moved, and now marked as an error
    mock_move.assert_not_called()
    self.assertIn((1, 'hello', 'Cannot move to project hello (file already present at /tmp/fake/dst/hello/spdx/hello-2018-03-12.spdx)'), self.retriever.results["error"])
