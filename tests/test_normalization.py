from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from roll.app.config import Config
from roll.app.diagnostics import run_doctor
from roll.app.normalization import (
    NamingStrategy,
    apply_keyword_vocab_fixes,
    apply_normalization_plan,
    build_safe_rename_plan,
    collect_keyword_vocab_fixes,
)
from roll.app.search import RollIndex
from roll.app.roll_store import RollMetadata, save_roll_metadata


class NormalizationTests(unittest.TestCase):
    def test_safe_rename_plan_detects_dot_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            year = archive / "2025"
            year.mkdir()
            (year / "10.19").mkdir()

            plan = build_safe_rename_plan(archive)

            self.assertEqual(len(plan.rules), 1)
            self.assertEqual(plan.rules[0].folder, year / "10.19")
            self.assertEqual(plan.rules[0].target, year / "10-19")

    def test_apply_normalization_plan_renames_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            year = archive / "2025"
            roll = year / "10.19"
            roll.mkdir(parents=True)

            plan = build_safe_rename_plan(archive)
            apply_normalization_plan(plan)

            self.assertTrue((year / "10-19").exists())
            self.assertFalse(roll.exists())

    def test_naming_strategy_builds_folder_name_from_loaded_at(self) -> None:
        self.assertEqual(NamingStrategy.build_folder_name("2025-10-19"), "10-19")

    def test_doctor_flags_non_uppercase_keywords(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            year = archive / "2025"
            roll = year / "10-19"
            roll.mkdir(parents=True)

            save_roll_metadata(
                roll / "roll.toml",
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=["friends"],
                ),
            )

            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(any("uppercase" in issue.message for issue in report.issues))

    def test_doctor_collects_missing_keywords_for_vocab_fix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            year = archive / "2025"
            roll = year / "10-19"
            roll.mkdir(parents=True)

            save_roll_metadata(
                roll / "roll.toml",
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=["FIRE"],
                ),
            )

            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")

            self.assertEqual(collect_keyword_vocab_fixes(archive), ["FIRE"])

    def test_apply_keyword_vocab_fixes_writes_keywords_dictionary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")

            path = apply_keyword_vocab_fixes(archive, ["FIRE", "EASTER"])

            self.assertEqual(path, vocabulary / "keywords.txt")
            self.assertEqual((vocabulary / "keywords.txt").read_text(encoding="utf-8"), "EASTER\nFIRE\n")

    def test_doctor_flags_lowercase_keywords_in_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (vocabulary / "keywords.txt").write_text("spring\nsummer\nWALK\n", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(any("uppercase" in issue.message for issue in report.issues))

    def test_doctor_flags_workspace_config_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text('archive = "/wrong/archive"\n', encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(any("Workspace config" in issue.message for issue in report.issues))

    def test_count_roll_statuses_groups_loaded_processed_failed(self) -> None:
        from roll.cli import _count_roll_statuses

        rolls = [
            RollIndex(Path("a"), "loaded", "", "", "", [], []),
            RollIndex(Path("b"), "processed", "", "", "", [], []),
            RollIndex(Path("c"), "failed", "", "", "", [], []),
            RollIndex(Path("d"), "processed", "", "", "", [], []),
        ]

        self.assertEqual(_count_roll_statuses(rolls), {"loaded": 1, "processed": 2, "failed": 1})
