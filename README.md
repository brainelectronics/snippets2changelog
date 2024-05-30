# snippets2changelog

[![Downloads](https://pepy.tech/badge/snippets2changelog)](https://pepy.tech/project/snippets2changelog)
![Release](https://img.shields.io/github/v/release/brainelectronics/snippets2changelog?include_prereleases&color=success)
![Python](https://img.shields.io/badge/python3-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/brainelectronics/snippets2changelog/branch/main/graph/badge.svg)](https://app.codecov.io/github/brainelectronics/snippets2changelog)

Generate a changelog from individual snippets

---------------


## General

Create version info files based on the latest changelog entry.

<!-- MarkdownTOC -->

- [Installation](#installation)
- [Usage](#usage)
  - [Info](#info)
  - [Create](#create)
  - [Parse](#parse)
- [Contributing](#contributing)
  - [Setup](#setup)
  - [Testing](#testing)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Installation

```bash
[<PYTHON> -m] pip[3] install [--user] [--upgrade] snippets2changelog
```

## Usage

### Info

Print informations about snippets2changelog

```bash
changelog-generator info
```

### Create

Create a new snippet with the given name at the specified snippets folder

```bash
changelog-generator create example_snippets/123.md
```

```
Short description: My example snippet
Choose from: ['bugfix', 'feature', 'breaking']
Type of change: feature
Choose from: ['internal', 'external', 'all']
Scope of change: external
Affected users (default all): testers
```

```
## My example snippet
<!--
type: feature
scope: external
affected: testers, users
-->

TBD

```

### Parse

Parse an existing snippet file and return the data as JSON without indentation

```bash
changelog-generator parse example_snippets/123.md \
  --indent=4
```

```json
{
    "type": "feature",
    "scope": [
        "external"
    ],
    "affected": [
        "testers",
        "users"
    ],
    "title": "My example snippet",
    "details": "\n\nTBD\n"
}
```

## Contributing

### Setup

For active development you need to have `poetry` and `pre-commit` installed

```bash
python3 -m pip install --upgrade --user poetry pre-commit
git clone https://github.com/brainelectronics/snippets2changelog.git
cd snippets2changelog
pre-commit install
poetry install
```

### Testing

```bash
# run all tests
poetry run coverage run -m pytest -v

# run only one specific tests
poetry run coverage run -m pytest -v -k "test_read_save_json"
```

Generate the coverage files with

```bash
python create_report_dirs.py
coverage html
```

The coverage report is placed at `reports/coverage/html/index.html`

## Credits

A big thank you to the creators and maintainers of [SemVer.org][ref-semver]
for their documentation and [regex example][ref-semver-regex-example]

<!-- Links -->
[ref-semver]: https://semver.org/
[ref-semver-regex-example]: https://regex101.com/r/Ly7O1x/3/
