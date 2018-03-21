# projectdb.py
#
# Module to interact with project databases for spdxLicenseManager.
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
import datetime

from sqlalchemy import create_engine, desc, extract, and_
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError
from sqlalchemy.orm import sessionmaker

from .__configs__ import (isValidConfigKey, isInternalConfigKey,
  getConfigKeyDesc)
from .datatypes import (Base, Category, Config, Conversion, File, License,
  Scan, Subproject)

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

class ProjectDBDeleteError(Exception):
  """Exception raised for errors in database deletions.

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

    ##### Placeholder: Other data/config insertion functions could be
    ##### called here, if desired

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

  ######################
  ##### Config functions
  ######################

  def getConfigsAll(self):
    return self.session.query(Config).order_by(Config.key).all()

  def getConfigValue(self, key):
    config = self.session.query(Config).filter(Config.key == key).first()
    if config:
      return config.value
    else:
      raise ProjectDBQueryError(f"Configuration value not found for '{key}'.")

  def setConfigValue(self, key, value):
    if not isValidConfigKey(key):
      raise ProjectDBInsertError(f"Cannot set configuration value for unknown key '{key}'.")
    if isInternalConfigKey(key):
      raise ProjectDBUpdateError(f"Cannot modify configuration value for reserved key '{key}'.")
    try:
      # check to see whether the key is already present
      config = self.session.query(Config).filter(Config.key == key).first()
      # if we get here, key was present, so we'll update it
      config.value = value
    except AttributeError:
      # if we get here instead, key did not exist, so we'll create it
      config = Config(key=key, value=value)
      self.session.add(config)
    # and regardless of whether or not it existed, commit it
    self.session.commit()
    return key

  def unsetConfigValue(self, key):
    if not isValidConfigKey(key):
      raise ProjectDBDeleteError(f"Cannot remove configuration value for unknown key '{key}'.")
    if isInternalConfigKey(key):
      raise ProjectDBDeleteError(f"Cannot remove configuration value for reserved key '{key}'.")
    config = self.session.query(Config).filter(Config.key == key).first()
    if config is None:
      raise ProjectDBDeleteError(f"Cannot remove configuration value for key '{key}', because it is not currently set.")
    self.session.delete(config)
    self.session.commit()

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

  def addSubproject(self, name, desc, *, spdx_search=None, commit=True):
    if not spdx_search:
      spdx_search = name
    subproject = Subproject(name=name, desc=desc, spdx_search=spdx_search)
    self.session.add(subproject)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return subproject._id

  def changeSubprojectSPDXSearch(self, name, spdx_search):
    # find out the order value for name
    subproject = self.session.query(Subproject).\
                              filter(Subproject.name == name).first()
    if subproject is None:
      raise ProjectDBUpdateError(f"Subproject {name} not found in changeSubprojectSPDXSearch")

    try:
      subproject.spdx_search = spdx_search
      self.session.commit()
    except IntegrityError:
      raise ProjectDBUpdateError(f"Subproject with SPDX search string {spdx_search} already exists in changeSubprojectSPDXSearch({name})")

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

  def getLicensesAllByCategory(self):
    query = self.session.query(
      Category._id, Category.name, Category.order, License.name
    ).join(License).order_by(Category.order, License.name).all()
    cat_lics = []
    for q in query:
      # just retain category and license names
      t = (q[1], q[3])
      cat_lics.append(t)
    return cat_lics

  def getLicensesInCategory(self, category):
    # raise exception if category does not exist
    cat = self.session.query(Category).\
                       filter(Category.name == category).first()
    if cat is None:
      raise ProjectDBQueryError(f"Category '{category}' does not exist.")

    return self.session.query(
      License._id, License.name
    ).join(Category).order_by(License.name).filter(
      Category.name == category
    ).all()

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

  def getLicenseMaxID(self):
    licenses = self.session.query(License._id).order_by(License._id)
    return max([license._id for license in licenses])

  def getMultipleLicenses(self, licenses):
    l_tup = self.session.query(License.name, License._id).\
                         filter(License.name.in_(licenses)).all()
    ldict = dict(l_tup)
    # make sure any items in licenses that weren't found are added as 'None'
    licensesAll = set(licenses)
    licensesFound = set(ldict.keys())
    licensesNotFound = licensesAll.difference(licensesFound)
    for lnf in licensesNotFound:
      ldict[lnf] = None
    return ldict

  def changeLicenseName(self, name, newName):
    if name is None or newName is None:
      raise ProjectDBUpdateError("Missing parameter for changeLicenseName")
    lic = self.session.query(License).\
                       filter(License.name == name).first()
    if lic is None:
      raise ProjectDBUpdateError(f"License {name} not found in changeLicenseName")

    try:
      lic.name = newName
      self.session.commit()
    except IntegrityError:
      raise ProjectDBUpdateError(f"License {newName} already exists in changeLicenseName({name})")

  def changeLicenseCategory(self, name, newCat):
    if name is None or newCat is None:
      raise ProjectDBUpdateError("Missing parameter for changeLicenseCategory")

    # get the category's ID for updating
    cat = self.session.query(Category).\
                       filter(Category.name == newCat).first()
    if cat is None:
      raise ProjectDBUpdateError(f"Category '{newCat}' does not exist.")
    category_id = cat._id

    lic = self.session.query(License).\
                       filter(License.name == name).first()
    if lic is None:
      raise ProjectDBUpdateError(f"License {name} not found in changeLicenseCategory")

    try:
      lic.category_id = category_id
      self.session.commit()
    except IntegrityError:
      raise ProjectDBUpdateError(f"Unexpected invalid category ID {category_id} in changeLicenseCategory")

  ##########################
  ##### Conversion functions
  ##########################

  def getConversionsAll(self):
    return self.session.query(Conversion).order_by(Conversion.old_text).all()

  def getConversion(self, *, _id=None, old_text=None):
    if _id is None and old_text is None:
      raise ProjectDBQueryError("Cannot call getConversion without either _id or old_text parameters")
    if _id is not None and old_text is not None:
      raise ProjectDBQueryError("Cannot call getConversion with both _id and old_text parameters")
    if _id is not None:
      return self.session.query(Conversion).\
                          filter(Conversion._id == _id).first()
    if old_text is not None:
      return self.session.query(Conversion).\
                          filter(Conversion.old_text == old_text).first()

  def addConversion(self, old_text, new_license, commit=True):
    # get the new license's ID for insertion
    lic = self.session.query(License).\
                       filter(License.name == new_license).first()
    if lic is None:
      raise ProjectDBInsertError(f'License "{new_license}" does not exist.')
    new_license_id = lic._id

    conv = Conversion(old_text=old_text, new_license_id=new_license_id)
    try:
      self.session.add(conv)
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except IntegrityError:
      raise ProjectDBInsertError(f"Conversion '{old_text}' already exists.")
    return conv._id

  def changeConversion(self, old_text, new_license):
    if old_text is None or new_license is None:
      raise ProjectDBUpdateError("Missing parameter for changeConversion")

    # get the new license's ID for updating
    lic = self.session.query(License).\
                       filter(License.name == new_license).first()
    if lic is None:
      raise ProjectDBUpdateError(f"License '{new_license}' does not exist.")
    new_license_id = lic._id

    conv = self.session.query(Conversion).\
                       filter(Conversion.old_text == old_text).first()
    if conv is None:
      raise ProjectDBUpdateError(f"Conversion {old_text} not found in changeConversion")

    try:
      conv.new_license_id = new_license_id
      self.session.commit()
    except IntegrityError:
      raise ProjectDBUpdateError(f"Unexpected invalid license ID {new_license_id} for license {new_license} in changeConversion")

  ####################
  ##### Scan functions
  ####################

  def getScansAll(self):
    return self.session.query(Scan).order_by(Scan._id).all()

  def getScansFiltered(self, *, subproject=None, month_tuple=None):
    if subproject is None and month_tuple is None:
      raise ProjectDBQueryError("Cannot call getScansFiltered without either subproject or month_tuple parameters")

    query = self.session.query(Scan)

    if subproject is not None:
      # get subproject ID if needed
      # or raise exception if subproject does not exist
      subprj = self.session.query(Subproject).\
                            filter(Subproject.name == subproject).first()
      if subprj is None:
        raise ProjectDBQueryError(f"Subproject '{subproject}' does not exist.")
      subprj_id = subprj._id
      query = query.filter(Scan.subproject_id == subprj_id)

    if month_tuple is not None:
      # confirm format is valid
      if not (isinstance(month_tuple, tuple) and
              len(month_tuple) == 2 and
              isinstance(month_tuple[0], int) and
              isinstance(month_tuple[1], int)):
        raise ProjectDBQueryError(f"Filter requires month in form (year, month)")
      yr = month_tuple[0]
      mt = month_tuple[1]
      query = query.filter(and_(
        extract('year', Scan.scan_dt) == yr,
        extract('month', Scan.scan_dt) == mt,
      ))

    return query.order_by(Scan._id).all()

  def getScan(self, _id):
    return self.session.query(Scan).\
                        filter(Scan._id == _id).first()

  def addScan(self, subproject, scan_dt_str, desc, commit=True):
    # get the subproject's ID for insertion
    subprj = self.session.query(Subproject).\
                          filter(Subproject.name == subproject).first()
    if subprj is None:
      raise ProjectDBInsertError(f'Subproject "{subproject}" does not exist.')
    subproject_id = subprj._id

    # parse the scan date string for insertion
    try:
      scan_dt = datetime.datetime.strptime(scan_dt_str, "%Y-%m-%d")
    except ValueError:
      raise ProjectDBInsertError("Scan date must be in format YYYY-MM-DD")

    scan = Scan(subproject_id=subproject_id, scan_dt=scan_dt, desc=desc)
    self.session.add(scan)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return scan._id

  ####################
  ##### File functions
  ####################

  def getFiles(self, scan_id):
    if scan_id is None:
      raise ProjectDBQueryError("Cannot call getFiles without a scan ID")

    # raise exception if scan does not exist
    scan = self.session.query(Scan).\
                        filter(Scan._id == scan_id).first()
    if scan is None:
      raise ProjectDBQueryError(f"Scan ID '{scan_id}' does not exist.")

    return self.session.query(File).\
                        filter(File.scan_id == scan_id).\
                        order_by(File.path).all()

  def getFile(self, *, _id=None, scan_id=None, path=None):
    if _id is None and (scan_id is None or path is None):
      raise ProjectDBQueryError("Cannot call getFile without required params")

    if _id is not None and (scan_id is not None or path is not None):
      raise ProjectDBQueryError("Cannot call getFile with both ID and other params")

    query = self.session.query(File)
    if _id is not None:
      return query.filter(File._id == _id).first()
    else:
      return query.filter(and_(File.scan_id == scan_id,
                               File.path == path)).first()

  def addFile(self, *, scan_id, path, license_id,
      sha1=None, md5=None, sha256=None, commit=True):
    file = File(scan_id=scan_id, path=path, license_id=license_id,
      sha1=sha1, md5=md5, sha256=sha256)
    self.session.add(file)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
    return file._id

  def addBulkFiles(self, *, scan_id, file_tuples, commit=True):
    """
    Add multiple files with one function call.
    file_tuples is a list of tuples in the following order:
      ft[0]: path
      ft[1]: license ID
      ft[2]: SHA1   (can be None)
      ft[3]: MD5    (can be None)
      ft[4]: SHA256 (can be None)
    """
    files = []
    for ft in file_tuples:
      file = File(
        scan_id=scan_id,
        path=ft[0],
        license_id=ft[1],
        sha1=ft[2],
        md5=ft[3],
        sha256=ft[4]
      )
      files.append(file)
    self.session.bulk_save_objects(files)
    if commit:
      self.session.commit()
    else:
      self.session.flush()
