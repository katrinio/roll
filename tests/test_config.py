from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from roll.app.diagnostics.diagnostics import run_doctor
from roll.app.diagnostics import diagnostics as diagnostics_module
from roll.app.diagnostics.doctor_output import render_doctor
from roll.app.workspace import config as config_module
from roll.app.workspace.config import Config, load_config, save_config, set_lang
from roll.messages import Msg


class ConfigTests(unittest.TestCase):
    def test_save_and_load_config_roundtrip_with_lang(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            original = Config(
                archives=[Path("/tmp/archive-a"), Path("/tmp/archive-b")], lang="EN"
            )

            save_config(original)

            loaded = load_config()
            self.assertEqual(loaded, original)

    def test_set_lang_updates_existing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            save_config(Config(archives=[Path("/tmp/archive")], lang="RU"))

            updated = set_lang("EN")

            self.assertEqual(updated.lang, "EN")
            self.assertEqual(load_config().lang, "EN")

    def test_load_config_defaults_to_en_when_lang_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            config_module.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            config_module.CONFIG_FILE.write_text(
                'lang = "DE"\narchives = ["/tmp/archive"]\n',
                encoding="utf-8",
            )

            loaded = load_config()

            self.assertEqual(loaded.lang, "EN")

    def test_load_config_requires_toml_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)

            with self.assertRaises(FileNotFoundError):
                load_config()

    def test_message_reflects_lang_change_without_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            self._patch_message_home(tmp)
            save_config(Config(archives=[Path("/tmp/archive")], lang="EN"))

            self.assertEqual(str(Msg.LANGUAGE), "Language:")

            set_lang("RU")

            self.assertEqual(str(Msg.LANGUAGE), "Язык:")

    def test_doctor_warns_when_language_is_not_set_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            archive = Path(tmp) / "archive"
            archive.mkdir()
            config_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            diagnostics_module.CONFIG_FILE = config_module.CONFIG_FILE
            config_module.CONFIG_FILE.write_text(
                f'archives = ["{archive}"]\n',
                encoding="utf-8",
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    "Language is not set explicitly" in issue.message
                    for issue in report.issues
                )
            )

    def test_doctor_reports_invalid_language_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            archive = Path(tmp) / "archive"
            archive.mkdir()
            config_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            diagnostics_module.CONFIG_FILE = config_module.CONFIG_FILE
            config_module.CONFIG_FILE.write_text(
                f'lang = "ENщ"\narchives = ["{archive}"]\n',
                encoding="utf-8",
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    issue.message.startswith("Invalid global config language:")
                    for issue in report.issues
                )
            )

    def test_doctor_warns_on_duplicate_archives_in_global_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            archive = Path(tmp) / "archive"
            archive.mkdir()
            config_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            diagnostics_module.CONFIG_FILE = config_module.CONFIG_FILE
            config_module.CONFIG_FILE.write_text(
                f'lang = "EN"\narchives = ["{archive}", "{archive}"]\n',
                encoding="utf-8",
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    "duplicate archives" in issue.message.lower()
                    for issue in report.issues
                )
            )

    def test_doctor_errors_when_global_config_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)

            report = run_doctor(Config(archives=[]))

            self.assertTrue(
                any(
                    "Missing global config file" in issue.message
                    for issue in report.issues
                )
            )

    def test_doctor_groups_issues_by_workspace_when_multiple_archives_exist(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            self._patch_message_home(tmp)

            first = Path(tmp) / "archive-a"
            second = Path(tmp) / "archive-b"
            for archive in (first, second):
                archive.mkdir()
                workspace = archive / ".roll"
                vocabulary = workspace / "vocabulary"
                vocabulary.mkdir(parents=True)
                for name in ("films", "cameras", "features", "keywords"):
                    (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
                (workspace / "config.toml").write_text("", encoding="utf-8")
            config_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            diagnostics_module.CONFIG_FILE = config_module.CONFIG_FILE
            config_module.CONFIG_FILE.write_text(
                f'archives = ["{first}", "{second}"]\n',
                encoding="utf-8",
            )

            buffer = StringIO()
            with redirect_stdout(buffer):
                render_doctor()

            output = buffer.getvalue()
            self.assertIn("Global config", output)
            self.assertIn(f"Workspace {first}", output)
            self.assertIn(f"Workspace {second}", output)

    def _patch_config_paths(self, tmp: str) -> None:
        config_module.CONFIG_DIR = Path(tmp) / ".config" / "roll"
        config_module.CONFIG_FILE = config_module.CONFIG_DIR / "config.toml"
        diagnostics_module.CONFIG_FILE = config_module.CONFIG_FILE

    def _patch_message_home(self, tmp: str) -> None:
        patcher = patch("roll.messages.cli.Path.home", return_value=Path(tmp))
        self.addCleanup(patcher.stop)
        patcher.start()
