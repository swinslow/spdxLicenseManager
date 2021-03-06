# Makefile
#
# Makefile for spdxLicenseManager, primarily used for running tests.
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

test: unittest functest

functest: FORCE
	python -m unittest discover -s tests -p "ft_*.py"

unittest: FORCE
	python -m unittest discover -s tests -p "unit_*.py"

%.py: FORCE
	python -m unittest discover -s tests -p $@

coverage: FORCE
	coverage run --source slm -m unittest discover -s tests -p "*.py"

coverage_report: coverage
	coverage report -m

FORCE:
