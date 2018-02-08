**Note**: this is an in-process rewrite of [spdxSummarizer](https://github.com/swinslow/spdxSummarizer), designed to be more scriptable, configurable and backed by a full test suite. It is **not** yet ready for prime-time, as much of the plumbing is still very much in process.

# spdxLicenseManager

[![Build Status](https://travis-ci.org/swinslow/spdxLicenseManager.svg?branch=master)](https://travis-ci.org/swinslow/spdxLicenseManager) [![Coverage Status](https://coveralls.io/repos/github/swinslow/spdxLicenseManager/badge.svg?branch=master)](https://coveralls.io/github/swinslow/spdxLicenseManager?branch=master)

## About

spdxLicenseManager is a set of command-line tools for importing, analyzing and generating reports about files and licenses.

It imports [SPDX®](https://spdx.org/) tag-value files, and processes, categorizes and reports on its license data in various formats.

## Licenses for spdxLicenseManager

Different licenses apply to different portions of this repository's contents:
- The spdxLicenseManager source code is released under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0), Apache-2.0, a copy of which can be found in the file [`LICENSE-code.txt`](LICENSE-code.txt).
- The spdxLicenseManager documentation is released under the [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/), CC-BY-4.0, a copy of which can be found in the file [`LICENSE-docs.txt`](LICENSE-docs.txt).
- The `tests/testfiles/` directory contains sample SPDX files used in the spdxLicenseManager test suite. As required by section 2.2 of the [SPDX specification](https://spdx.org/spdx-specification-21-web-version), these SPDX files are provided under the [Creative Commons CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/), CC0-1.0, a copy of which can be found in the file [`LICENSE-spdxfiles.txt`](LICENSE-spdxfiles.txt).

This README.md file is documentation, and therefore gets the following:

```
Copyright (C) The Linux Foundation
SPDX-License-Identifier: CC-BY-4.0
```
