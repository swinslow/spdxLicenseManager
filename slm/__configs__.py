# __configs__.py
#
# Single source for valid Config keys for spdxLicenseManager project DBs.
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

# tuple format:
# [0]: key name
# [1]: internal config value? (e.g., can't be modified or deleted by user)
# [2]: description

__valid_configs__ = [

  # System configuration keys
  ('magic', True, 'Magic number to validate spdxLicenseManager database'),
  ('initialized', True, 'Is this spdxLicenseManager database initialized?'),

  # Importer configurations
  ('import-strip-path-prefixes', False, 'Remove common file path prefixes from a scan before importing?'),

  # Analyzer configurations; intended to be overridable on command line
  ('analyze-extensions', False, 'Flag: Analyze file extensions (for "No license found" results)'),
  ('analyze-extensions-list', False, 'Semicolon-separated string: If analyze-extensions is set, list of file extensions to analyze'),
  ('analyze-thirdparty', False, 'Flag: Analyze file paths for "third party" directories'),
  ('analyze-thirdparty-dirs', False, 'Semicolon-separated string: If analyze-thirdparty is set, list of directories to analyze'),
  ('analyze-emptyfile', False, 'Flag: Analyze file checksums for empty files'),
  ('analyze-exclude-path-prefix', False, 'Flag: Exclude common path prefixes from reports'),

  # Reporter configurations; intended to be overridable on command line
  ('report-include-summary', False, 'Flag: Include summary page in reports'),
  ('report-strip-licenseref', False, 'Remove "LicenseRef-" tags from licenses in reports?'),
]

def isValidConfigKey(key):
  for (config_key, internal, desc) in __valid_configs__:
    if config_key == key:
      return True
  return False

def isInternalConfigKey(key):
  for (config_key, internal, desc) in __valid_configs__:
    if config_key == key:
      return internal
  return False

def getConfigKeyDesc(key):
  for (config_key, internal, desc) in __valid_configs__:
    if config_key == key:
      return desc
  return None
