# datatypes.py
#
# Module with SQLAlchemy data type definitions for spdxLicenseManager.
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

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Config(Base):
  __tablename__ = 'config'
  key = Column(String(), primary_key=True)
  value = Column(String())

  def __repr__(self):
    return f"Config {self.key} => {self.value}"

class Subproject(Base):
  __tablename__ = 'subprojects'
  _id = Column(Integer(), primary_key=True)
  name = Column(String())
  desc = Column(String())

  def __repr__(self):
    return f"Subproject {self._id}: {self.name} ({self.desc})"

class Category(Base):
  __tablename__ = 'categories'
  _id = Column(Integer(), primary_key=True)
  name = Column(String(), unique=True)
  order = Column(Integer())

  def __repr__(self):
    return f"Category {self._id}, order {self.order}: {self.name}"

class License(Base):
  __tablename__ = 'licenses'
  # columns
  _id = Column(Integer(), primary_key=True)
  name = Column(String(), unique=True)
  category_id = Column(Integer(), ForeignKey('categories._id'))
  # relationships
  category = relationship("Category",
    backref=backref('licenses', order_by=name)
  )

  def __repr__(self):
    return f"License {self._id}: {self.name}, category {self.category.name}"

class Conversion(Base):
  __tablename__ = 'conversions'
  # columns
  _id = Column(Integer(), primary_key=True)
  old_text = Column(String(), unique=True)
  new_license_id = Column(Integer(), ForeignKey('licenses._id'))
  # relationships
  new_license = relationship('License',
    backref=backref('conversions', order_by=old_text)
  )

  def __repr__(self):
    return f"Conversion {self._id}: '{self.old_text}' => '{self.new_license.name}'"

class Scan(Base):
  __tablename__ = 'scans'
  # columns
  _id = Column(Integer(), primary_key=True)
  scan_dt = Column(Date())
  desc = Column(String())
  subproject_id = Column(Integer(), ForeignKey('subprojects._id'))
  # relationships
  subproject = relationship('Subproject',
    backref=backref('scans', order_by=_id)
  )

  def __repr__(self):
    return f"Scan {self._id}: {self.scan_dt}, {self.desc}"

class File(Base):
  __tablename__ = 'files'
  # columns
  _id = Column(Integer(), primary_key=True)
  path = Column(String())
  md5 = Column(String())
  sha1 = Column(String())
  sha256 = Column(String())
  scan_id = Column(Integer(), ForeignKey('scans._id'))
  license_id = Column(Integer(), ForeignKey('licenses._id'))
  # relationships
  scan = relationship('Scan',
    backref=backref('files', order_by=path)
  )
  license = relationship('License',
    backref=backref('files', order_by=path)
  )

  def __repr__(self):
    if self.license:
      lic_name = self.license.name
    else:
      lic_name = "NULL"
    return f"File {self._id}: scan {self.scan_id}, path {self.path}, license {lic_name} ({self.license_id})"
