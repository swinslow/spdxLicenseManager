# commands/helperContext.py
#
# Helper functions for spdxLicenseManager commands to extract context vars.
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

def extractContext(ctx):
  """Extract standard config vars from click context."""
  slmhome = ctx.obj.get('SLMHOME', None)
  mainconfig = ctx.obj.get('SLMCONFIG_DATA', None)
  project = ctx.obj.get('PROJECT', None)
  db = ctx.obj.get('PROJECTDB', None)

  return (slmhome, mainconfig, project, db)
