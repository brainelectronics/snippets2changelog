#!/usr/bin/env python3

"""Snippets parser"""

import logging
import re
from pathlib import Path

from .common import LOG_LEVELS, read_file

COMMENT_PATTERN = r"^<!--\n((.|\n)*?)\n-->$"


class SnippetParserError(Exception):
    """Base class for exceptions in this module."""

    pass


class SnippetParser(object):
    """docstring for SnippetCreator"""

    def __init__(self, file_name: Path, additional_keys: tuple[str] | tuple[()] = (), verbosity: int = 0) -> None:
        if file_name.exists():
            self._file_name = file_name
        else:
            raise SnippetParserError(f"Given snippets '{file_name}' does not exist")

        self._required_keys = ("type", "scope", "affected") + additional_keys
        self._content = dict(zip(self._required_keys, [""] * len(self._required_keys)))

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=LOG_LEVELS[min(verbosity, max(LOG_LEVELS.keys()))])

    @property
    def content(self) -> dict[str, str]:
        return self._content

    def parse(self) -> None:
        file_content = read_file(self._file_name, parse="read")

        header_match = re.search(r"(^##\s)(.*)", file_content, re.MULTILINE)
        if header_match:
            self._content["title"] = header_match.groups()[-1]

        matches = re.finditer(COMMENT_PATTERN, file_content, re.MULTILINE)
        match_found = False

        for match in matches:
            end = match.end()
            self._logger.debug(f"match: \n{match.group()}")
            found_keys = list()
            for key in self._required_keys:
                info_matches = re.finditer(rf"({key}:\s)(.*)", match.group(), re.MULTILINE)
                for key_match in info_matches:
                    data = key_match.groups()[-1]
                    if key in ("affected", "scope"):
                        data = [x.strip() for x in data.split(",")]

                    # do not overwrite already existing data
                    if not self._content[key]:
                        self._content[key] = data
                        found_keys.append(key)
                    self._logger.debug(f"processed: '{key}' as '{data}', found_keys: {found_keys}")

                if sorted(self._required_keys) == sorted(found_keys):
                    self._logger.debug("All required keys found, taking everything else as details content")
                    match_found = True
            if match_found:
                self._content["details"] = file_content[end:]
                break
