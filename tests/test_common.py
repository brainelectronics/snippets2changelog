#!/usr/bin/env python3

import json
import logging
from pathlib import Path
from typing import Any, Dict, Union

import pytest
from pytest import MonkeyPatch

from snippets2changelog.common import (
    LOG_LEVELS,
    collect_user_choice,
    read_file,
    save_file,
)


def test_log_levels() -> None:
    assert LOG_LEVELS[0] == logging.CRITICAL
    assert LOG_LEVELS[1] == logging.ERROR
    assert LOG_LEVELS[2] == logging.WARNING
    assert LOG_LEVELS[3] == logging.INFO
    assert LOG_LEVELS[4] == logging.DEBUG


def test_something_that_involves_user_input(monkeypatch: MonkeyPatch) -> None:
    # monkeypatch the "input" function, so that it returns "feature".
    # This simulates the user entering "feature" in the terminal:
    monkeypatch.setattr('builtins.input', lambda _: "feature")

    assert "feature" == collect_user_choice(question="what's it", options=["bugfix", "feature", "breaking"])


@pytest.mark.parametrize(
    "name, data",
    [
        ("json", {"a": 1, "b": ["2", 3], "c": {"d": 4}}),
        ("yml", {"a": 1, "b": ["2", 3], "c": {"d": 4}}),
        ("yaml", {"a": 1, "b": ["2", 3], "c": {"d": 4}}),
        ("txt", "Hello World"),
        ("txt", "Hello World\nFrom testing"),
        ("raise", "Something"),
    ]
)
def test_read_save_json(name: str, data: Union[Dict[str, Any], str], tmp_path: Path) -> None:
    p = tmp_path / f"data.{name}"

    if name == "raise":
        with pytest.raises(NotImplementedError):
            save_file(content=data, path=p, render=name)
    else:
        save_file(content=data, path=p, render=name)

    if name == "txt":
        name = "read"
        if "\n" in data:
            name = "readline"

    if name == "raise":
        with pytest.raises(NotImplementedError):
            assert read_file(path=p, parse=name) == data
    else:
        assert read_file(path=p, parse=name) == data if name != "readline" else data.split()
    assert len(list(tmp_path.iterdir())) == 1
