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

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from .datatypes import Config

class ProjectDBConfigError(Exception):
  def __init__(self, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)

class ProjectDB:
  def __init__(self):
    super(ProjectDB, self).__init__()
    self.engine = None
    self.session = None

  def createDatabase(self, pathToDB):
    if pathToDB != ":memory:":
      # check whether file already exists
      if os.path.exists(pathToDB):
        raise ProjectDBConfigError

    # create engine string (in-memory OR file path)
    engine_str = "sqlite:///" + pathToDB
    # create database and connect to it
    self.engine = create_engine(engine_str)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

  def isOpened(self):
    return (self.engine is not None and self.session is not None)

  def isInitialized(self):
    try:
      query = self.session.query(Config).\
                           filter(Config.key == "initialized").\
                           first()
      return query is not None and query.value == "yes"
    except OperationalError:
      return False
