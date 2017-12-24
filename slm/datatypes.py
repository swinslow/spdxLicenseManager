# datatypes.py
#
# Module with SQLAlchemy data type definitions for spdxLicenseManager.
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

from sqlalchemy import Column, Integer, String
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
