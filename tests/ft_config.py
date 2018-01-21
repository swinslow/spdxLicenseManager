# tests/ft_config.py
#
# Functional test for spdxLicenseManager: list, set and unset project
# configuration key/value pairs.
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

import unittest
import click
from click.testing import CliRunner

from slm import slm

from helper_sandbox import (setUpSandbox, runSandboxCommands, tearDownSandbox,
  runcmd, printResultDebug)

class ConfigFuncTestSuite(unittest.TestCase):
  """spdxLicenseManager configuration list, set and unset FT suite."""

  def setUp(self):
    self.runner = CliRunner()
    setUpSandbox(self, slm.cli)
    runSandboxCommands(self, slm.cli)

  def tearDown(self):
    tearDownSandbox(self)

  def test_can_set_and_get_a_new_config_value(self):
    # Edith wants to set a configuration variable and confirm it worked
    result = runcmd(self, slm.cli, "frotz", "set-config",
      "ignore_extensions", ".json;.png;.jpg;.jpeg;.gif")

    # It works correctly and lets her know
    self.assertEqual(0, result.exit_code)
    self.assertEqual("Configuration value set for 'ignore_extensions'.\n",
      result.output)

    # She retrieves the config value to make sure, and there it is
    result = runcmd(self, slm.cli, "frotz", "get-config", "ignore_extensions")
    self.assertEqual(0, result.exit_code)
    self.assertEqual("ignore_extensions: .json;.png;.jpg;.jpeg;.gif\n",
      result.output)

  def test_cannot_set_values_for_reserved_config_keys(self):
    # Edith accidentally tries to set a config variable with a reserved,
    # unmodifiable key
    result = runcmd(self, slm.cli, "frotz", "set-config", "magic", "hi")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot modify configuration value for key 'magic'.\n",result.output)

    # She tries it again for the 'initialized' reserved config value
    result = runcmd(self, slm.cli, "frotz", "set-config", "initialized", "hi")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot modify configuration value for key 'initialized'.\n",result.output)

  def test_cannot_set_value_for_unknown_config_key(self):
    # Edith accidentally tries to set a config variable with an unknown key
    result = runcmd(self, slm.cli, "frotz", "set-config", "invalid", "hi")

    # It fails and explains why
    self.assertEqual(1, result.exit_code)
    self.assertEqual("Cannot set configuration value for unknown key 'invalid'.\n",result.output)

  def test_can_list_configs(self):
    # Edith wants to get a list of all config keys and values
    result = runcmd(self, slm.cli, "frotz", "list-config")

    # they are sorted alphabetically, with asterisks for internal config
    self.assertEqual(0, result.exit_code)
    self.assertEqual("* initialized: yes\n* magic: spdxLicenseManager\nstrip_LicenseRef: yes\nvendor_dirs: vendor;thirdparty;third-party\n",
      result.output)
