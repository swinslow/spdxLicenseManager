# projectdb.py
#
# Module to interact with project databases for spdxLicenseManager.
#
# Copyright (C) The Linux Foundation
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
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from sqlalchemy.orm import sessionmaker

from .datatypes import Base, Category, Config, License, Subproject

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

class ProjectDBInsertError(Exception):
  """Exception raised for errors in database insertions.

  Attributes:
    message -- explanation of the error
  """
  def __init__(self, message):
    self.message = message

class ProjectDBUpdateError(Exception):
  """Exception raised for errors in database updates.

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

  ##########################
  ##### Subproject functions
  ##########################

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

  ########################
  ##### Category functions
  ########################

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
    highest = self.session.query(Category.order).\
                           order_by(desc(Category.order)).first()
    if highest is None:
      return 0
    return highest[0]

  def addCategory(self, name, order=None, commit=True):
    if order is None:
      order = self.getCategoryHighestOrder() + 1
    if order <= 0:
      raise ProjectDBInsertError(f"Cannot create category '{name}' with order {order}; order value must be a positive integer.")
    # check that order isn't already present
    catCheck = self.session.query(Category).\
                            filter(Category.order == order).first()
    if catCheck is not None:
      raise ProjectDBInsertError(f"Cannot create category '{name}' with order {order} because category '{catCheck.name}' already has order {order}.")

    category = Category(name=name, order=order)
    self.session.add(category)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return category._id

  def changeCategoryName(self, name, newName):
    if name is None or newName is None:
      raise ProjectDBUpdateError("Missing parameter for changeCategoryName")
    cat = self.session.query(Category).\
                       filter(Category.name == name).first()
    if cat is None:
      raise ProjectDBUpdateError(f"Category {name} not found in changeCategoryName")

    try:
      cat.name = newName
      self.session.commit()
    except IntegrityError:
      raise ProjectDBUpdateError(f"Category {newName} already exists in changeCategoryName({name})")

  def changeCategoryOrder(self, name, sortBefore):
    # find out the order value for name
    catMain = self.session.query(Category).\
                           filter(Category.name == name).first()
    if catMain is None:
      raise ProjectDBUpdateError(f"Category {name} not found in changeCategoryOrder")
    orderMain = catMain.order

    # temporarily change catMain's order to what should be an unused value,
    # so that we can reorder without breaking the unique constraint
    catMain.order = -999

    # find out the order value for sortBefore
    catSortBefore = self.session.query(Category).\
                                 filter(Category.name == sortBefore).first()
    if catSortBefore is None:
      raise ProjectDBUpdateError(f"Cannot sort '{name}' category before non-existent '{sortBefore}' category")
    orderSortBefore = catSortBefore.order

    if orderMain > orderSortBefore:
      # if orderMain is currently higher, then it's moving to a lower number.
      # all categories with values between these two, including sortBefore,
      # will be incremented
      cats = self.session.query(Category).filter(
        Category.order >= orderSortBefore,
        Category.order < orderMain
      ).all()
      for cat in cats:
        cat.order = cat.order + 1
      newMainOrder = orderSortBefore
    else:
      # if orderMain is currently lower, then it's moving to a higher number.
      # all categories with values between these two, NOT including sortBefore,
      # will be decremented
      cats = self.session.query(Category).filter(
        Category.order < orderSortBefore,
        Category.order > orderMain
      ).all()
      for cat in cats:
        cat.order = cat.order - 1
      newMainOrder = orderSortBefore - 1

    # now update the main category's order
    catMain.order = newMainOrder

    # and save everything
    self.session.commit()

  #######################
  ##### License functions
  #######################

  def getLicensesAll(self):
    return self.session.query(License).order_by(License.name).all()

  def addLicense(self, name, category, commit=True):
    # get the category's ID for insertion
    cat = self.session.query(Category).\
                            filter(Category.name == category).first()
    if cat is None:
      raise ProjectDBInsertError(f"Category '{category}' does not exist.")
    category_id = cat._id

    license = License(name=name, category_id=category_id)
    try:
      self.session.add(license)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except IntegrityError:
      raise ProjectDBInsertError(f"License '{name}' already exists.")
    return license._id

  def getLicense(self, *, _id=None, name=None):
    if _id is None and name is None:
      raise ProjectDBQueryError("Cannot call getLicense without either _id or name parameters")
    if _id is not None and name is not None:
      raise ProjectDBQueryError("Cannot call getLicense with both _id and name parameters")
    if _id is not None:
      return self.session.query(License).\
                          filter(License._id == _id).first()
    if name is not None:
      return self.session.query(License).\
                          filter(License.name == name).first()
