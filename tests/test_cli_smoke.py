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

    def test_batch_help(self) -> None:
        result = self._run("batch", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("process", self._output(result))

    def test_stats_help(self) -> None:
        result = self._run("stats", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Год", self._output(result))

    def test_config_lang_shows_current_language(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            config_dir = Path(home) / ".config" / "roll"
            config_dir.mkdir(parents=True)
            (config_dir / "config.toml").write_text(
                'lang = "EN"\narchives = ["/tmp/archive"]\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [PYTHON, "-c", CLI_ENTRY, "config", "lang"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("EN", self._output(result))

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
