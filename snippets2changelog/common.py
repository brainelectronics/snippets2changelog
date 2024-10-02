#!/usr/bin/env python3

"""Common helper functions"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

LOG_LEVELS = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}


def collect_user_choice(question: str, options: List[str]) -> str:
    while True:
        print(f"Choose from: {options}")
        choice = input(question if question.endswith(": ") else question + ": ")
        if choice in options:
            return choice
        else:
            print(f"Invalid input: '{choice}', choose from: {options}")


def read_file(path: Path, parse: str = "read", mode: str = "r") -> Union[Dict[Any, Any], str, List[str], Any]:
    with open(path, mode) as file:
        if parse == "read":
            return file.read()
        elif parse == "readline":
            return file.readline()
        elif parse == "json":
            return json.load(file)
        elif parse in ["yml", "yaml"]:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise exc
        else:
            raise NotImplementedError(
                "Only 'read', 'readline', 'json' or 'yaml' are valid parse options"
            )


def save_file(content: Union[str, Dict[Any, Any]], path: Path, mode: str = "w", render: str = "txt") -> None:
    """
    Save a file to the specified path with the given content.

    The file and its parent directories will be created if necessary
    """
    Path(path.parent).mkdir(parents=True, exist_ok=True)

    # save rendered file
    with open(path, mode) as file:
        if render == "txt":
            file.write(content)
        elif render == "json":
            json.dump(content, file)
        elif render in ("yml", "yaml"):
            yaml.dump(content, file, default_flow_style=False)
        else:
            raise NotImplementedError("Only 'txt', 'json' or 'yaml' are valid render options")
