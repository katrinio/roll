from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from roll.app.workspace import config as config_module
from roll.app.workspace.config import Config, load_config, save_config, set_lang
from roll.messages import Msg


class ConfigTests(unittest.TestCase):
    def test_save_and_load_config_roundtrip_with_lang(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            original = Config(archives=[Path("/tmp/archive-a"), Path("/tmp/archive-b")], lang="EN")

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

    def test_load_config_defaults_to_ru_when_lang_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            config_module.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            config_module.CONFIG_FILE.write_text(
                'lang = "DE"\narchives = ["/tmp/archive"]\n',
                encoding="utf-8",
            )

            loaded = load_config()

            self.assertEqual(loaded.lang, "RU")

    def test_message_reflects_lang_change_without_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._patch_config_paths(tmp)
            self._patch_message_home(tmp)
            save_config(Config(archives=[Path("/tmp/archive")], lang="RU"))

            self.assertEqual(str(Msg.LANGUAGE), "Язык:")

            set_lang("EN")

            self.assertEqual(str(Msg.LANGUAGE), "Language:")

    def _patch_config_paths(self, tmp: str) -> None:
        config_module.CONFIG_DIR = Path(tmp) / ".config" / "roll"
        config_module.CONFIG_FILE = config_module.CONFIG_DIR / "config.toml"

    def _patch_message_home(self, tmp: str) -> None:
        patcher = patch("roll.messages.cli.Path.home", return_value=Path(tmp))
        self.addCleanup(patcher.stop)
        patcher.start()
