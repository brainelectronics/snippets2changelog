#!/usr/bin/env python3

"""snippets2changelog - CLI"""

import importlib.metadata
import json
import logging
from argparse import ArgumentParser
from argparse import Namespace as Args
from pathlib import Path
from sys import stdout
from typing import Sequence

from .common import LOG_LEVELS, collect_user_choice
from .creator import SnippetCreator
from .parser import SnippetParser

LOGGER_FORMAT = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s @'\
                ' %(funcName)-15s:%(lineno)4s] %(message)s'

# configure logging
logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT, stream=stdout)

logger = logging.getLogger("snippets2changelog")
logger.setLevel(logging.DEBUG)


def does_exist(parser: ArgumentParser, arg: str) -> Path:
    if not Path(arg).resolve().exists():
        parser.error(f"{Path(arg).resolve()} does not exist")
    else:
        return Path(arg)


def parse_args(argv: Sequence[str] | None = None) -> Args:
    """Multi command argument parser"""
    parser = ArgumentParser(__doc__)
    parser.add_argument(
        "--verbose", "-v",
        default=0,
        action="count",
        help="Set level of verbosity, default is CRITICAL",
    )

    subparsers = parser.add_subparsers(required=True, help="available commands", dest="command")

    parser_info = subparsers.add_parser(
        "info",
        help="Prints information about snippets2changelog",
    )
    parser_info.set_defaults(func=fn_info)

    parser_create = subparsers.add_parser(
        "create",
        help="Create a snippet",
    )
    parser_create.set_defaults(func=fn_create)
    parser_create.add_argument(
        "name",
        type=Path,
        help="Name of new snippet",
    )

    parser_parse = subparsers.add_parser(
        "parse",
        help="Parse a snippet",
    )
    parser_parse.set_defaults(func=fn_parse)
    parser_parse.add_argument(
        "name",
        type=lambda x: does_exist(parser, x),
        help="Path to snippet",
    )
    parser_parse.add_argument(
        "--indent",
        type=int,
        default=None,
        help="Print with indentation",
    )

    subparsers.help = f"[{' '.join(str(c) for c in subparsers.choices)}]"

    return parser.parse_args(argv)


def extract_version() -> str:
    """Returns version of installed package or the one of version.py"""
    try:
        from .version import __version__

        return f"{__version__}-dev"
    except ImportError:
        return importlib.metadata.version("snippets2changelog")


def fn_info(_args: Args) -> None:
    print(f"Version: {extract_version()}")


def fn_create(args: Args) -> None:
    content = {
        "short_description": input("Short description: "),
        "type": collect_user_choice(
            question="Type of change", options=["bugfix", "feature", "breaking"]
        ),
        "scope": collect_user_choice(question="Scope of change", options=["internal", "external", "all"]),
        "affected": input("Affected users (default all): ") or "all",
        "content": "TBD",
    }
    sc = SnippetCreator(file_name=args.name, content=content)
    logger.debug(f"rendered content: >>>>>>\n{sc.render()}\n<<<<<<")
    sc.create()


def fn_parse(args: Args) -> None:
    sp = SnippetParser(file_name=args.name, verbosity=args.verbose)
    sp.parse()
    print(json.dumps(sp.content, indent=args.indent))


def main() -> int:
    """Entry point for everything else"""
    args = parse_args()

    log_level = LOG_LEVELS[min(args.verbose, max(LOG_LEVELS.keys()))]
    logger.setLevel(level=log_level)
    logger.debug(f"{args}, {log_level}")

    args.func(args)

    return 0


if __name__ == "__main__":
    main()
