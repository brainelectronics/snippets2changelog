#!/usr/bin/env python3

"""Snippets generator"""

import logging
from pathlib import Path
from typing import Dict, Iterator

from changelog2version.extract_version import ExtractVersion  # type: ignore
from git import Commit
from jinja2 import Environment, FileSystemLoader

from .collector import SnippetCollector
from .common import LOG_LEVELS, read_file, save_file
from .parser import SnippetParser


class SnippetCreatorError(Exception):
    """Base class for exceptions in this module."""

    pass


class ChangelogCreatorError(Exception):
    """Base class for exceptions in this module."""

    pass


class SnippetCreator(object):
    """docstring for SnippetCreator"""

    def __init__(self, verbosity: int = 0) -> None:
        self._required_render_keys = ("short_description", "type", "scope", "affected", "content")
        self._rendered_content = ""

        self._template_folder = (Path(__file__).parent / "templates").resolve()
        self._snippet_template = "snippet.md.template"

        self._env = Environment(
            loader=FileSystemLoader(searchpath=self._template_folder),
            keep_trailing_newline=True
        )

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=LOG_LEVELS[min(verbosity, max(LOG_LEVELS.keys()))])

    @property
    def rendered_content(self) -> str:
        return self._rendered_content

    def render(self, content: Dict[str, str]) -> None:
        if all(k in content for k in self._required_render_keys):
            self._rendered_content = self._env.get_template(str(self._snippet_template)).render(content)
        else:
            raise SnippetCreatorError(
                f"Not all required keys are given to render the snippet. Required keys: {self._required_render_keys}"
            )

    def create(self, file_name: Path) -> None:
        save_file(content=self.rendered_content, path=file_name)


class ChangelogCreator(ExtractVersion, SnippetParser, SnippetCreator, SnippetCollector):  # type: ignore
    """docstring for ChangelogCreator"""

    def __init__(self, changelog: Path,  snippets_folder: Path, update_in_place: bool, skip_internal: bool = False, verbosity: int = 0) -> None:
        if changelog.exists():
            self._changelog = changelog
            self._update_in_place = update_in_place
        else:
            raise ChangelogCreatorError(f"Given changelog '{changelog}' does not exist")

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=LOG_LEVELS[min(verbosity, max(LOG_LEVELS.keys()))])

        ExtractVersion.__init__(self, logger=self._logger)
        SnippetParser.__init__(self, verbosity=verbosity)
        SnippetCreator.__init__(self, verbosity=verbosity)
        SnippetCollector.__init__(self, snippets_folder=snippets_folder)

        self._version_line = self.parse_changelog(changelog_file=self._changelog)
        self._logger.debug(f"version_line: {self._version_line}")
        # "## [0.1.0] - 2024-05-30"

        _ = self.parse_semver_line(release_version_line=self._version_line)
        self._logger.debug(("semver_data:", self.semver_data))
        # VersionInfo(major=0, minor=1, patch=0, prerelease=None, build=None))

        self._skip_internal = skip_internal

    def update_changelog(self) -> None:
        new_changelog_content = ""
        # create a "prolog" and an "epilog", with the new content in between
        existing_changelog_content = read_file(path=self._changelog, parse="read").split(self._version_line)

        for commit, file_name in self.snippets():
            self._logger.debug(f"Parsing {file_name}")
            self.parse(file_name=file_name)
            snippet_content = self.parsed_content
            self._logger.debug(snippet_content)

            if "internal" in snippet_content["scope"] and self._skip_internal:
                continue

            if snippet_content["type"] == "bugfix":
                self.semver_data = self.semver_data.bump_patch()
            elif snippet_content["type"] == "feature":
                self.semver_data = self.semver_data.bump_minor()
            elif snippet_content["type"] == "breaking":
                self.semver_data = self.semver_data.bump_major()
            else:
                raise ChangelogCreatorError(f"Invalid version change type: {snippet_content['type']}")

            changelog_entry_content = {
                "version": self.semver_data,
                "timestamp": commit.committed_datetime.isoformat(),
                "meta": {
                    "type": snippet_content["type"],
                    "scope": snippet_content["scope"],
                    "affected": snippet_content["affected"],
                },
                "content": snippet_content["details"],
                "version_reference": f"https://github.com/brainelectronics/snippets2changelog/tree/{self.semver_data}",
            }
            self._logger.debug(f"changelog_entry_content: {changelog_entry_content}")

            changelog_entry = self._env.get_template("changelog_part.md.template").render(changelog_entry_content)
            self._logger.debug(f"rendered changelog_entry: \n{changelog_entry}")
            new_changelog_content = changelog_entry + new_changelog_content

        rendered_changelog = self._env.get_template("changelog.md.template").render({"prolog": existing_changelog_content[0], "new": new_changelog_content, "existing": self._version_line + existing_changelog_content[1]})
        rendered_changelog_path = Path(f"{self._changelog}")
        if not self._update_in_place:
            rendered_changelog_path = Path(str(rendered_changelog_path) + ".new")
        save_file(content=rendered_changelog, path=rendered_changelog_path)
