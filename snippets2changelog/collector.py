#!/usr/bin/env python3

"""Snippets collector"""

from collections.abc import Iterator
from pathlib import Path
from typing import List, Tuple

from git import Commit, GitCmdObjectDB, Repo, Submodule, TagReference
from git.refs.head import Head


class CollectorError(Exception):
    """Base class for exceptions in this module."""

    pass


class HistoryWalker(object):
    """docstring for HistoryWalker"""

    def __init__(
        self, repo: Path, search_parent_directories: bool = True, branch_only: bool = True
    ) -> None:
        if repo.exists():
            try:
                self._repo = Repo(repo, search_parent_directories=search_parent_directories)
            except Exception as e:
                raise CollectorError(e)
        else:
            raise CollectorError(f"Given repo folder '{repo}' does not exist")

        # limit amount of commits to crawl to a positive number
        self._max_count = None
        self._branch_only = branch_only

    @property
    def repo_root(self) -> Path:
        return Path(self._repo.working_dir)

    @property
    def branch_name(self) -> str:
        try:
            return str(self._repo.active_branch)
        except Exception as e:
            print(f"HEAD is detached: {e}")
            return str(self._repo.head.commit.hexsha)

    @property
    def tags(self) -> List[TagReference]:
        return sorted(self._repo.tags, key=lambda t: t.commit.committed_datetime)

    def commits(self) -> Iterator[Commit]:
        kwargs = dict()

        if self._branch_only:
            # Collect the commits on this branch only
            # aka ignore commits on other branches
            kwargs["first-parent"] = True

        # latest commit is first element
        for ele in self._repo.iter_commits(
            rev=self.branch_name,
            max_count=self._max_count,
            **kwargs,
        ):
            yield ele


class SnippetCollector(HistoryWalker):
    """docstring for SnippetCollector"""

    def __init__(self, snippets_folder: Path, file_extension: str = "md", **kwargs) -> None:
        if snippets_folder.exists():
            self._snippets_folder = snippets_folder
        else:
            raise CollectorError(f"Given snippets folder '{snippets_folder}' does not exist")

        HistoryWalker.__init__(self, repo=self._snippets_folder, **kwargs)
        self._file_extension = file_extension

    @property
    def snippets_folder(self) -> Path:
        return self._snippets_folder

    def all_snippet_files(self) -> Iterator[Path]:
        """Get all potential snippet files from the snippets folder"""
        for file in self._snippets_folder.iterdir():
            if file.is_file() and (file.suffix == ".{}".format(self._file_extension)):
                yield file

    def snippets(self) -> Iterator[Tuple[Commit, Path]]:
        collected_snippets = list(self.all_snippet_files())

        # nice chaos :)
        # close to midnight, stop now or the problem of tomorrow will catch you

        # self._logger.debug(f"Repo root: {self.repo_root}")
        # changelog-generator/

        # self._logger.debug(f"collected_snippets: {collected_snippets}, looking for {self.snippets_folder}")
        # collected_snippets: [PosixPath('.snippets/3.md')], looking for .snippets

        # use reversed to have oldest commit as first element
        for idx, commit in reversed(list(enumerate(self.commits()))):
            for file in commit.stats.files.keys():
                # self._logger.debug(f"{idx}: {commit}, looking for file: {file} in {collected_snippets}")
                # 0: b768d6983432b730d81b34d125a4bbefb0a66525, looking for file: .snippets/3.md in [PosixPath('.snippets/3.md')]
                # self._logger.debug(Path(file) in collected_snippets)
                # True
                """
                if self.snippets_folder / file in collected_snippets:
                    self._logger.warning(f"file {self.snippets_folder / file} is a match")
                    yield (commit, self.snippets_folder / file)
                """
                if Path(file) in collected_snippets:
                    # self._logger.debug(f"file {file} is a match")
                    # file .snippets/3.md is a match
                    yield (commit, Path(file))
