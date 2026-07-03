from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CLI_ENTRY = "from roll.cli import app; app()"


class CliSmokeTests(unittest.TestCase):
    def test_root_help(self) -> None:
        result = self._run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("stock", self._output(result))
        self.assertIn("features", self._output(result))

    def test_stock_help(self) -> None:
        result = self._run("stock", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("add", self._output(result))
        self.assertIn("load", self._output(result))

    def test_features_help(self) -> None:
        result = self._run("features", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("add", self._output(result))

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        with tempfile.TemporaryDirectory() as home:
            env["HOME"] = home
            return subprocess.run(
                [PYTHON, "-c", CLI_ENTRY, *args],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def _output(self, result: subprocess.CompletedProcess[str]) -> str:
        return result.stdout + result.stderr
