#!/usr/bin/env python3

"""Snippets generator"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .common import LOG_LEVELS, save_file


class SnippetCreatorError(Exception):
    """Base class for exceptions in this module."""

    pass


class SnippetCreator(object):
    """docstring for SnippetCreator"""

    def __init__(self, file_name: Path, content: dict[str, str], verbosity: int = 0) -> None:
        _required_keys = ("short_description", "type", "scope", "affected", "content")
        if all(k in content for k in _required_keys):
            self._snippet_content = content
        else:
            raise SnippetCreatorError(
                f"Not all required keys are given to render the snippet. Required keys: {_required_keys}"
            )

        self._file_name = file_name
        self._template_folder = (Path(__file__).parent / "templates").resolve()
        self._snippet_template = "snippet.md.template"

        self._env = Environment(
            loader=FileSystemLoader(searchpath=self._template_folder), keep_trailing_newline=True
        )

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=LOG_LEVELS[min(verbosity, max(LOG_LEVELS.keys()))])

    @property
    def snippets_file(self) -> Path:
        return self._file_name

    @property
    def content(self) -> dict[str, str]:
        return self._snippet_content

    def render(self) -> str:
        return self._env.get_template(str(self._snippet_template)).render(self.content)

    def create(self) -> None:
        save_file(content=self.render(), path=self.snippets_file)
