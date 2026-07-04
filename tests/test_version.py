from __future__ import annotations

import unittest
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

from roll.version import get_version, is_outdated


class VersionTests(unittest.TestCase):
    def test_get_version_falls_back_to_git_tag(self) -> None:
        get_version.cache_clear()
        with (
            patch("roll.version.package_version", side_effect=PackageNotFoundError),
            patch("roll.version._git_tag", return_value="0.4.0"),
        ):
            self.assertEqual(get_version(), "0.4.0")

    def test_git_tag_search_uses_current_worktree(self) -> None:
        get_version.cache_clear()
        with (
            patch("roll.version.package_version", side_effect=PackageNotFoundError),
            patch("roll.version.Path.cwd", return_value=Path("/repo/worktree")),
            patch("roll.version._find_git_root", return_value=Path("/repo/worktree")),
            patch("roll.version.subprocess.run") as run,
        ):
            run.return_value.returncode = 0
            run.return_value.stdout = "v0.4.1\n"
            self.assertEqual(get_version(), "0.4.1")

    def test_is_outdated_compares_versions(self) -> None:
        self.assertTrue(is_outdated(current="0.4.0", latest="0.4.1"))
        self.assertFalse(is_outdated(current="0.4.1", latest="0.4.1"))
        self.assertFalse(is_outdated(current="0.4.2", latest="0.4.1"))
