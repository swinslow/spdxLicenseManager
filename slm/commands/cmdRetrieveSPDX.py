# commands/cmdRetrieveSPDX.py
#
# Implementation of 'retrieve-spdx' command for spdxLicenseManager.
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
from ..projectdb import ProjectDBQueryError

from ..retriever import Retriever

def cmdRetrieveSPDX(ctx, month):
  slmhome, mainconfig, project, db = extractContext(ctx)

  # check whether spdx-search-dir is set
  try:
    search_dir = db.getConfigValue("spdx-search-dir")
  except ProjectDBQueryError as e:
    sys.exit("Configuration variable for SPDX search directory not found.\nPlease call 'slm set-config spdx-search-dir DIR_NAME' first.")

  retriever = Retriever()

  # get subprojects
  subprojects = db.getSubprojectsAll()

  # get project dir
  project_dir = os.path.join(slmhome, "projects", project)

  # set config
  retriever.setDatestr(month)
  retriever.setSearchDir(search_dir)
  retriever.setProjectDir(project_dir)
  for subproject in subprojects:
    retriever.addSubproject(
      name=subproject.name,
      _id=subproject._id,
      spdx_search=subproject.spdx_search,
    )

  # run retriever
  retriever.prepareFiles()
  retriever.createResults()
  retriever.moveFiles()

  # output results
  for _id, name, srcPath, dstPath in retriever.results["success"]:
    srcFile = os.path.split(srcPath)[1]
    dstFile = os.path.split(dstPath)[1]
    click.echo(f"Moved {srcFile} to {name} (new name: {dstFile})")
