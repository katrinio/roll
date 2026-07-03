from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from roll.app.normalization import NamingStrategy, apply_normalization_plan, build_safe_rename_plan
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

