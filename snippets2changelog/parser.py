#!/usr/bin/env python3

"""Snippets parser"""

import logging
import re
from pathlib import Path
from typing import Dict, Tuple, Union

from .common import LOG_LEVELS, read_file

COMMENT_PATTERN = r"^<!--\n((.|\n)*?)\n-->$"


class SnippetParserError(Exception):
    """Base class for exceptions in this module."""

    pass


class SnippetParser(object):
    """docstring for SnippetCreator"""

    def __init__(self, additional_keys: Union[Tuple[str], Tuple[()]] = (), verbosity: int = 0) -> None:
        self._file_name = Path()
        self._required_parser_keys = ("type", "scope", "affected") + additional_keys
        self._parsed_content = dict(zip(self._required_parser_keys, [""] * len(self._required_parser_keys)))
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=LOG_LEVELS[min(verbosity, max(LOG_LEVELS.keys()))])

    @property
    def parsed_content(self) -> Dict[str, str]:
        return self._parsed_content

    def parse(self, file_name: Path) -> None:
        # don't forget to clear the content before the next run
        self._parsed_content = dict(zip(self._required_parser_keys, [""] * len(self._required_parser_keys)))

        if not file_name.exists():
            raise SnippetParserError(f"Given snippets '{file_name}' does not exist")

        file_content = read_file(file_name, parse="read")

        header_match = re.search(r"(^##\s)(.*)", file_content, re.MULTILINE)
        if header_match:
            self._parsed_content["title"] = header_match.groups()[-1]

        matches = re.finditer(COMMENT_PATTERN, file_content, re.MULTILINE)
        match_found = False

        for match in matches:
            end = match.end()
            self._logger.debug(f"match: \n{match.group()}")
            found_keys = list()
            for key in self._required_parser_keys:
                info_matches = re.finditer(rf"({key}:\s)(.*)", match.group(), re.MULTILINE)
                for key_match in info_matches:
                    data = key_match.groups()[-1]
                    if key in ("affected", "scope"):
                        data = [x.strip() for x in data.split(",")]

                    # do not overwrite already existing data
                    if not self._parsed_content[key]:
                        self._parsed_content[key] = data
                        found_keys.append(key)
                    self._logger.debug(f"processed: '{key}' as '{data}', found_keys: {found_keys}, required: {self._required_parser_keys}")

                if sorted(self._required_parser_keys) == sorted(found_keys):
                    self._logger.debug("All required keys found, taking everything else as details content")
                    match_found = True
            if match_found:
                self._parsed_content["details"] = file_content[end:]
                break
