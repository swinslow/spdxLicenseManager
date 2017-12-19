# setup.py
#
# Python packaging config file for spdxLicenseManager.
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

from setuptools import setup, find_packages

# using single source version details per https://packaging.python.org/guides/single-sourcing-package-version/ option 3
version = {}
with open("slm/__about__.py") as fp:
  exec(fp.read(), version)

setup(
  name='spdxLicenseManager',
  version=version['__version__'],
  packages=find_packages(),
  install_requires=[
    'Click',
  ],
  entry_points='''
    [console_scripts]
    slm=slm.slm:cli
  ''',
)
