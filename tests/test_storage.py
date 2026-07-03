from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from roll.app.roll_store import RollMetadata, load_roll_metadata, save_roll_metadata, update_roll_features, update_roll_keywords
from roll.app.stock_store import StockItem, add_to_stock, load_stock, remove_from_stock, save_stock


class StockStoreTests(unittest.TestCase):
    def test_save_and_load_stock_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stock.toml"
            items = [StockItem("Kodak Gold 200", 3), StockItem("Ilford HP5 Plus", 1)]

            save_stock(path, items)

            self.assertEqual(load_stock(path), [StockItem("Ilford HP5 Plus", 1), StockItem("Kodak Gold 200", 3)])

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
