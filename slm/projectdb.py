# projectdb.py
#
# Module to interact with project databases for spdxLicenseManager.
#
# Copyright (C) 2017 The Linux Foundation
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

import os

class ProjectDBConfigError(Exception):
  def __init__(self, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)

class ProjectDB:
  def __init__(self):
    super(ProjectDB, self).__init__()

  def createDatabase(self, pathToDB):
    if pathToDB != ":memory:":
      # check whether file already exists
      if os.path.exists(pathToDB):
        raise ProjectDBConfigError
