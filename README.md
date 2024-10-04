# snippets2changelog

[![Downloads](https://pepy.tech/badge/snippets2changelog)](https://pepy.tech/project/snippets2changelog)
![Release](https://img.shields.io/github/v/release/brainelectronics/snippets2changelog?include_prereleases&color=success)
![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11-green.svg)
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
    - [Snippet](#snippet)
    - [Changelog](#changelog)
  - [Parse](#parse)
  - [CI](#ci)
    - [GitHub](#github)
      - [Actions](#actions)
      - [Custom workflow](#custom-workflow)
    - [Other](#other)
- [Contributing](#contributing)
  - [Setup](#setup)
  - [Testing](#testing)
  - [Changelog](#changelog-1)
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
#### Snippet

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

#### Changelog

Create or update a changelog with all snippets.

The generated changelog will be named `<OLD_CHANGELOG_NAME.new>` unless the
`--in-place` flag is used. This flag is intended for CI usage with a clean
checkout before a run.

*Be aware to restore the changelog before another run as it might generate
version entries and version bumps multiple times otherwise.*

```bash
changelog-generator changelog changelog.md --snippets=.snippets [--in-place]
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

### CI

To use this tool in a CI environment use the following commands, job configs or
actions.

#### GitHub
##### Actions
See [changelog-from-snippets](https://github.com/brainelectronics/changelog-from-snippets) action.

##### Custom workflow

```yaml
---
name: Generate changelog

on:
  push:
    branches:
      - main

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          # all history is needed to crawl it properly
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: |
          pip install snippets2changelog
      - name: Update changelog with snippets
        run: |
          changelog-generator \
            changelog changelog.md \
            --snippets=.snippets \
            --in-place
```

#### Other

```bash
pip install snippets2changelog
changelog-generator \
  changelog changelog.md \
  --snippets=.snippets \
  --in-place
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

### Changelog

The changelog format is based on [Keep a Changelog][ref-keep-a-changelog], and
this project adheres to [Semantic Versioning][ref-semantic-versioning].

Please add a changelog snippet, see above, for every PR you contribute. The
changes are categorised into:

- `bugfixes` fix an issue which can be used out of the box without any further
changes required by the user. Be aware that in some cases bugfixes can be
breaking changes.
- `features` is used to indicate a backwards compatible change providing
improved or extended functionalitiy. This does, as `bugfixes`, in any case
not require any changes by the user to keep the system running after upgrading.
- `breaking` creates a breaking, non backwards compatible change which
requires the user to perform additional tasks, adopt his currently running
code or in general can't be used as is anymore.

The changelog entry shall be short but meaningful and can of course contain
links and references to other issues or PRs. New lines are only allowed for a
new bulletpoint entry. Usage examples or other code snippets should be placed
in the code documentation, README or the docs folder.

## Credits

A big thank you to the creators and maintainers of [SemVer.org][ref-semver]
for their documentation and [regex example][ref-semver-regex-example]

<!-- Links -->
[ref-keep-a-changelog]: https://keepachangelog.com/en/1.0.0/
[ref-semantic-versioning]: https://semver.org/spec/v2.0.0.html
[ref-semver]: https://semver.org/
[ref-semver-regex-example]: https://regex101.com/r/Ly7O1x/3/
