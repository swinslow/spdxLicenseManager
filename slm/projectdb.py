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

from sqlalchemy import create_engine, desc
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.orm import sessionmaker

from .datatypes import Base, Category, Config, Subproject

class ProjectDBConfigError(Exception):
  """Exception raised for errors in database configuration.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class ProjectDBQueryError(Exception):
  """Exception raised for errors in database queries.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class ProjectDB:
  def __init__(self):
    super(ProjectDB, self).__init__()
    self.engine = None
    self.session = None

  def createDB(self, pathToDB):
    if pathToDB != ":memory:":
      # check whether file already exists
      if os.path.exists(pathToDB):
        raise ProjectDBConfigError(f"File {pathToDB} already exists, not re-creating it")

    # create engine string (in-memory OR file path)
    engine_str = "sqlite:///" + pathToDB
    # create database and connect to it
    self.engine = create_engine(engine_str)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

  def isOpened(self):
    return (self.engine is not None and self.session is not None)

  def isInitialized(self):
    if not self.isOpened():
      return False
    try:
      query = self.session.query(Config).\
                           filter(Config.key == "initialized").\
                           first()
      return query is not None and query.value == "yes"
    except OperationalError:
      return False

  def initializeDBTables(self):
    # create tables
    Base.metadata.create_all(self.engine)

    # insert basic config values, with initialized as "no" until other
    # insertions are completed
    c1 = Config(key="magic", value="spdxLicenseManager")
    c2 = Config(key="initialized", value="no")
    self.session.bulk_save_objects([c1, c2])
    self.session.commit()

    ##### FIXME CALL OTHER DATA INSERTION FUNCTIONS HERE

    # if we make it here (e.g. no exception was raised earlier), set
    # "initialized" to "yes"
    query = self.session.query(Config).filter(Config.key == "initialized")
    query.update({Config.value: "yes"})
    self.session.commit()

  def openDB(self, pathToDB):
    if pathToDB == ":memory:":
      raise ProjectDBConfigError(f"Can't open an in-memory database, call createDB() instead")

    # create engine string (file path only)
    engine_str = "sqlite:///" + pathToDB

    # connect to database
    self.engine = create_engine(engine_str)
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

    # query to confirm config magic value is valid
    try:
      query = self.session.query(Config).filter_by(key="magic").first()
    except DatabaseError:
      # file is not a database
      self.closeDB()
      raise ProjectDBConfigError(f"{pathToDB} is not an spdxLicenseManager database file")

    if query.value != "spdxLicenseManager":
      self.closeDB()
      raise ProjectDBConfigError(f"{pathToDB} does not contain spdxLicenseManager magic value")

  def closeDB(self):
    if self.session is not None:
      self.session.close()
      self.session = None
    self.engine = None

  def commit(self):
    self.session.commit()

  def rollback(self):
    self.session.rollback()

  ##### Subproject functions

  def getSubprojectsAll(self):
    return self.session.query(Subproject).order_by(Subproject.name).all()

  def getSubproject(self, *, _id=None, name=None):
    if _id is None and name is None:
      raise ProjectDBQueryError("Cannot call getSubproject without either _id or name parameters")
    if _id is not None and name is not None:
      raise ProjectDBQueryError("Cannot call getSubproject with both _id and name parameters")
    if _id is not None:
      return self.session.query(Subproject).\
                          filter(Subproject._id == _id).first()
    if name is not None:
      return self.session.query(Subproject).\
                          filter(Subproject.name == name).first()

  def addSubproject(self, name, desc, commit=True):
    subproject = Subproject(name=name, desc=desc)
    self.session.add(subproject)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return subproject._id

  ##### Category functions

  def getCategoriesAll(self):
    return self.session.query(Category).order_by(Category.order).all()

  def getCategory(self, *, _id=None, name=None):
    if _id is None and name is None:
      raise ProjectDBQueryError("Cannot call getCategory without either _id or name parameters")
    if _id is not None and name is not None:
      raise ProjectDBQueryError("Cannot call getCategory with both _id and name parameters")
    if _id is not None:
      return self.session.query(Category).\
                          filter(Category._id == _id).first()
    if name is not None:
      return self.session.query(Category).\
                          filter(Category.name == name).first()

  def getCategoryHighestOrder(self):
    return self.session.query(Category.order).\
                        order_by(desc(Category.order)).first()[0]

  def addCategory(self, name, order=None, commit=True):
    if order is None:
      order = self.getCategoryHighestOrder() + 1
    category = Category(name=name, order=order)
    self.session.add(category)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return category._id
