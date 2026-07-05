from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
import os

from roll.app.workspace.config import Config
from roll.app.diagnostics.diagnostics import run_doctor
from roll.app.archive.normalization import (
    NamingStrategy,
    apply_keyword_vocab_fixes,
    apply_normalization_plan,
    apply_normalization_plans,
    build_safe_rename_plan,
    build_photo_normalization_plan,
    collect_keyword_vocab_fixes,
    NormalizationPlan,
    RenameRule,
)
from roll.app.diagnostics.doctor_output import _echo_block
from roll.app.archive.photo_dates import guess_archive_month
from roll.app.archive.search import RollIndex
from roll.filesystem import build_archive_tree, count_photo_files
from roll.app.workspace.roll_store import RollMetadata, save_roll_metadata
from roll.cli import _build_photo_normalization_plans
from roll.helpers.output import echo_lines
from roll.messages import Normalize


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

    def test_guess_archive_month_uses_most_common_photo_month(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name, timestamp in (
                ("a.jpg", 1711929600),
                ("b.jpg", 1711929600),
                ("c.jpg", 1709251200),
            ):
                path = folder / name
                path.write_bytes(b"")
                os.utime(path, (timestamp, timestamp))

            guess = guess_archive_month(folder)

            self.assertIsNotNone(guess)
            self.assertEqual(guess.month_key, "2024-04")
            self.assertEqual(guess.confidence, 2)

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

            self.assertTrue(
                any("uppercase" in issue.message for issue in report.issues)
            )

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
            self.assertEqual(
                (vocabulary / "keywords.txt").read_text(encoding="utf-8"),
                "EASTER\nFIRE\n",
            )

    def test_build_photo_normalization_plan_uses_photo_month(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            folder = archive / "Фото"
            folder.mkdir()
            for name, timestamp in (
                ("a.jpg", 1711929600),
                ("b.jpg", 1711929600),
                ("c.jpg", 1709251200),
            ):
                path = folder / name
                path.write_bytes(b"")
                os.utime(path, (timestamp, timestamp))

            plan = build_photo_normalization_plan(archive)

            self.assertEqual(len(plan.rules), 1)
            self.assertEqual(plan.rules[0].folder, folder)
            self.assertEqual(plan.rules[0].target, archive / "2024" / "04-01")

    def test_apply_normalization_plans_creates_target_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            source = archive / "Фото"
            source.mkdir()
            plan = NormalizationPlan(
                archive=archive,
                rules=[RenameRule(folder=source, target=archive / "2023" / "09-01")],
                conflicts=[],
            )

            apply_normalization_plans([plan])

            self.assertTrue((archive / "2023").exists())
            self.assertTrue((archive / "2023" / "09-01").exists())

    def test_photo_normalize_prompts_are_localized_and_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            folders = [archive / "4770", archive / "4771"]
            for folder in folders:
                folder.mkdir()

            prompts: list[str] = []
            confirms: list[str] = []

            def record_prompt(text: str, *args, **kwargs):
                prompts.append(text)
                if "Month" in text or "Месяц" in text:
                    return "09" if "4770" in text else "03"
                if "Year" in text or "Год" in text:
                    return "2023"
                return "y"

            def record_confirm(text: str, *args, **kwargs):
                confirms.append(text)
                return len(confirms) > 1

            with (
                patch("roll.cli.guess_archive_year", return_value=2023),
                patch("roll.cli._photo_folders", return_value=folders),
                patch("roll.cli.typer.confirm", side_effect=record_confirm),
                patch("roll.cli.typer.prompt", side_effect=record_prompt),
            ):
                _build_photo_normalization_plans(archive)

            self.assertTrue(any("Year 2023 correct" in item for item in confirms))
            self.assertTrue(any("Month for 4770 [01-12]" in item for item in prompts))
            self.assertTrue(any("Month for 4771 [01-12]" in item for item in prompts))
            self.assertTrue(all("::" not in item for item in prompts))
            self.assertTrue(all("::" not in item for item in confirms))

    def test_echo_lines_renders_message_locale(self) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            echo_lines([Normalize.HEADER])

        self.assertEqual(buffer.getvalue().strip(), "Archive normalization")

    def test_doctor_flags_lowercase_keywords_in_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (vocabulary / "keywords.txt").write_text(
                "spring\nsummer\nWALK\n", encoding="utf-8"
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    "keywords.txt is not canonical" in issue.message
                    for issue in report.issues
                )
            )

    def test_doctor_flags_workspace_config_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text(
                'archive = "/wrong/archive"\n', encoding="utf-8"
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any("Workspace config" in issue.message for issue in report.issues)
            )

    def test_doctor_flags_missing_archive_in_workspace_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text("", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(any("archive" in issue.message for issue in report.issues))

    def test_doctor_flags_invalid_workspace_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text("archive = [\n", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    "workspace config" in issue.message.lower()
                    for issue in report.issues
                )
            )

    def test_doctor_flags_missing_stock_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text(
                f'archive = "{archive}"\n', encoding="utf-8"
            )

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any("stock.toml" in issue.message for issue in report.issues)
            )

    def test_doctor_flags_invalid_stock_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text(
                f'archive = "{archive}"\n', encoding="utf-8"
            )
            (workspace / "stock.toml").write_text("items = [\n", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any("stock.toml" in issue.message for issue in report.issues)
            )

    def test_doctor_flags_roll_loaded_at_mismatch(self) -> None:
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
                    loaded_at="2025-10-20",
                    features=[],
                    keywords=[],
                ),
            )

            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features", "keywords"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (workspace / "config.toml").write_text(
                f'archive = "{archive}"\n', encoding="utf-8"
            )
            (workspace / "stock.toml").write_text("", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any("loaded_at" in issue.message for issue in report.issues)
            )

    def test_doctor_flags_noncanonical_keywords_dictionary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            for name in ("films", "cameras", "features"):
                (vocabulary / f"{name}.txt").write_text("", encoding="utf-8")
            (vocabulary / "keywords.txt").write_text(
                "spring\nBAR\nspring\n", encoding="utf-8"
            )
            (workspace / "config.toml").write_text(
                f'archive = "{archive}"\n', encoding="utf-8"
            )
            (workspace / "stock.toml").write_text("", encoding="utf-8")

            report = run_doctor(Config(archives=[archive]))

            self.assertTrue(
                any(
                    "keywords.txt is not canonical" in issue.message
                    for issue in report.issues
                )
            )

    def test_doctor_renders_single_warning_once(self) -> None:
        with (
            patch("roll.app.diagnostics.doctor_output.echo") as echo_mock,
            patch(
                "roll.app.diagnostics.doctor_output.highlight_cli_names",
                side_effect=lambda value: value,
            ),
        ):
            _echo_block(
                "WARN:",
                ["keywords.txt is not canonical:"],
                {"keywords.txt is not canonical:": ["/tmp/keywords.txt"]},
            )

        rendered = [call.args[0] for call in echo_mock.call_args_list]
        self.assertEqual(
            rendered,
            [
                "WARN: 1",
                "  keywords.txt is not canonical: /tmp/keywords.txt",
            ],
        )

    def test_count_roll_statuses_groups_loaded_processed_failed(self) -> None:
        from roll.app.archive.stats import _count_statuses

        rolls = [
            RollIndex(Path("a"), "loaded", "", "", "", [], []),
            RollIndex(Path("b"), "processed", "", "", "", [], []),
            RollIndex(Path("c"), "failed", "", "", "", [], []),
            RollIndex(Path("d"), "processed", "", "", "", [], []),
        ]

        self.assertEqual(
            _count_statuses(rolls), {"loaded": 1, "processed": 2, "failed": 1}
        )

    def test_build_archive_tree_lists_years_and_rolls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            (archive / "2025" / "10-19").mkdir(parents=True)
            (archive / "2025" / "11-03").mkdir(parents=True)
            (archive / "2026" / "01-01").mkdir(parents=True)

            self.assertEqual(
                build_archive_tree(archive),
                ["2025", "  ├── 10-19", "  └── 11-03", "2026", "  └── 01-01"],
            )

    def test_count_photo_files_counts_common_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.jpg").write_text("", encoding="utf-8")
            (folder / "b.txt").write_text("", encoding="utf-8")
            (folder / "nested").mkdir()
            (folder / "nested" / "c.PNG").write_text("", encoding="utf-8")

            self.assertEqual(count_photo_files(folder), 2)
