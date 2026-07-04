from __future__ import annotations

import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from roll.version import get_version


class VersionTests(unittest.TestCase):
    def test_get_version_falls_back_to_git_tag(self) -> None:
        get_version.cache_clear()
        with (
            patch("roll.version.package_version", side_effect=PackageNotFoundError),
            patch("roll.version._git_tag", return_value="v0.4.0"),
        ):
            self.assertEqual(get_version(), "v0.4.0")
