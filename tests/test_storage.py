from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from roll.app.workspace.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
    update_roll_features,
    update_roll_keywords,
)
from roll.app.workspace.stock_store import (
    StockItem,
    add_to_stock,
    load_stock,
    remove_from_stock,
    save_stock,
)
from roll.app.archive.normalization import normalize_keywords_in_archive
from roll.app.flows.stock import _format_roll_label, _rolls, _prompt_roll_metadata
from roll.app.workspace.workspace import workspace_for


class StockStoreTests(unittest.TestCase):
    def test_save_and_load_stock_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stock.toml"
            items = [StockItem("Kodak Gold 200", 3), StockItem("Ilford HP5 Plus", 1)]

            save_stock(path, items)

            self.assertEqual(
                load_stock(path),
                [StockItem("Ilford HP5 Plus", 1), StockItem("Kodak Gold 200", 3)],
            )

    def test_add_to_stock_merges_case_insensitively(self) -> None:
        items = [StockItem("Kodak Gold 200", 1)]

        merged = add_to_stock(items, "kodak gold 200", 2)

        self.assertEqual(merged, [StockItem("Kodak Gold 200", 3)])

    def test_remove_from_stock_preserves_canonical_name(self) -> None:
        items = [StockItem("Kodak Gold 200", 3)]

        updated = remove_from_stock(items, "kodak gold 200", 1)

        self.assertEqual(updated, [StockItem("Kodak Gold 200", 2)])


class RollStoreTests(unittest.TestCase):
    def test_save_and_load_roll_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roll.toml"
            metadata = RollMetadata(
                status="loaded",
                film="Kodak Gold 200",
                camera="Pentax Espio 150SL",
                loaded_at="2025-10-19",
                features=["redscale"],
                keywords=["FRIENDS"],
            )

            save_roll_metadata(path, metadata)

            self.assertEqual(load_roll_metadata(path), metadata)

    def test_update_roll_keywords_normalizes_to_uppercase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roll.toml"
            save_roll_metadata(
                path,
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=[],
                ),
            )

            updated = update_roll_keywords(path, ["friends", "Friends", "BAR"])

            self.assertEqual(updated.keywords, ["FRIENDS", "BAR"])

    def test_update_roll_keywords_keeps_uppercase_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roll.toml"
            save_roll_metadata(
                path,
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=["friends"],
                ),
            )

            updated = update_roll_keywords(path, ["bar"])

            self.assertEqual(updated.keywords, ["FRIENDS", "BAR"])

    def test_update_roll_features_merges_unique_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roll.toml"
            save_roll_metadata(
                path,
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=["redscale"],
                    keywords=[],
                ),
            )

            updated = update_roll_features(path, ["redscale", "push +1"])

            self.assertEqual(updated.features, ["redscale", "push +1"])

    def test_normalize_keywords_in_archive_uppercases_roll_and_vocabulary(self) -> None:
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
                    keywords=["friends", "BAR"],
                ),
            )

            workspace = archive / ".roll"
            vocabulary = workspace / "vocabulary"
            vocabulary.mkdir(parents=True)
            (vocabulary / "keywords.txt").write_text("friends\nBAR\n", encoding="utf-8")

            normalize_keywords_in_archive(archive)

            self.assertEqual(
                load_roll_metadata(roll / "roll.toml").keywords,
                ["FRIENDS", "BAR"],
            )
            self.assertEqual(
                (vocabulary / "keywords.txt").read_text(encoding="utf-8"),
                "BAR\nFRIENDS\n",
            )

    def test_rolls_include_all_rolls_with_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            first = archive / "2025" / "10-19"
            second = archive / "2025" / "10-20"
            first.mkdir(parents=True)
            second.mkdir(parents=True)

            save_roll_metadata(
                first / "roll.toml",
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=[],
                    original_source="negative",
                    digital_copy="scan",
                    original_status="lost",
                ),
            )
            save_roll_metadata(
                second / "roll.toml",
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-20",
                    features=[],
                    keywords=[],
                ),
            )

            self.assertEqual(_rolls(archive), [first, second])

    def test_roll_label_is_short_and_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            roll = archive / "2025" / "10-19"
            roll.mkdir(parents=True)
            save_roll_metadata(
                roll / "roll.toml",
                RollMetadata(
                    status="loaded",
                    film="Kodak Gold 200",
                    camera="Pentax Espio 150SL",
                    loaded_at="2025-10-19",
                    features=[],
                    keywords=[],
                    original_source="negative",
                    digital_copy="scan",
                    original_status="lost",
                ),
            )

            label = _format_roll_label(roll)

            self.assertEqual(
                label, "2025/10-19 | Kodak Gold 200 | Pentax Espio 150SL | loaded"
            )

    def test_roll_edit_prompt_can_update_all_metadata_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp)
            workspace = workspace_for(archive)
            for name in ("films", "cameras", "features", "keywords"):
                workspace.dictionary(name).write([])

            metadata = RollMetadata(
                status="loaded",
                film="Kodak Gold 200",
                camera="Pentax Espio 150SL",
                loaded_at="2025-10-19",
                features=["redscale"],
                keywords=["FRIENDS"],
                original_source="negative",
                digital_copy="scan",
                original_status="lost",
            )

            prompts = iter(
                [
                    "Kodak ColorPlus 200",
                    "Pentax K1000",
                    "push +1, expired",
                    "summer, beach",
                ]
            )
            prompts = iter(
                [
                    "Kodak ColorPlus 200",
                    "Pentax K1000",
                    "2",
                    "push +1, expired",
                    "summer, beach",
                    "2",
                    "2",
                    "1",
                ]
            )

            def fake_prompt(*args, **kwargs):
                return next(prompts)

            with (
                patch("roll.app.flows.stock.prompt", side_effect=fake_prompt),
            ):
                updated = _prompt_roll_metadata(
                    archive, archive / "2025/10-19/roll.toml", metadata
                )

            self.assertEqual(updated.film, "Kodak ColorPlus 200")
            self.assertEqual(updated.camera, "Pentax K1000")
            self.assertEqual(updated.status, "processed")
            self.assertEqual(updated.features, ["redscale", "push +1", "expired"])
            self.assertEqual(updated.keywords, ["FRIENDS", "SUMMER", "BEACH"])
            self.assertEqual(updated.original_source, "slide")
            self.assertEqual(updated.digital_copy, "photo")
            self.assertEqual(updated.original_status, "present")
