#!/usr/bin/env python3

"""snippets2changelog - CLI"""

import importlib.metadata
import json
import logging
from argparse import ArgumentParser
from argparse import Namespace as Args
from pathlib import Path
from sys import stdout
from typing import Sequence, Union

from .common import LOG_LEVELS, collect_user_choice
from .creator import ChangelogCreator, SnippetCreator
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


def parse_args(argv: Union[Sequence[str], None] = None) -> Args:
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

    parser_changelog = subparsers.add_parser(
        "changelog",
        help="Create a changelog",
    )
    parser_changelog.set_defaults(func=fn_changelog)
    parser_changelog.add_argument(
        "changelog",
        type=Path,
        help="Path to existing changelog",
    )
    parser_changelog.add_argument(
        "--snippets",
        type=lambda x: does_exist(parser, x),
        help="Directory to crawl for snippets",
    )
    parser_changelog.add_argument(
        "--in-place",
        action='store_true',
        help="Update specified changelog in place",
    )
    parser_changelog.add_argument(
        "--no-internal",
        action='store_true',
        help="Skip snippets with scope set as 'internal'",
    )

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


def fn_changelog(args: Args) -> None:
    cc = ChangelogCreator(changelog=args.changelog, snippets_folder=args.snippets, update_in_place=args.in_place, skip_internal=args.no_internal, verbosity=args.verbose)
    cc.update_changelog()


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
    sc = SnippetCreator()
    sc.render(content=content)
    logger.debug(f"rendered content: >>>>>>\n{sc.rendered_content}\n<<<<<<")
    sc.create(file_name=args.name)


def fn_parse(args: Args) -> None:
    sp = SnippetParser(verbosity=args.verbose)
    sp.parse(file_name=args.name)
    print(json.dumps(sp.parsed_content, indent=args.indent))


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
