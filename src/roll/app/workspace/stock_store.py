from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class StockItem:
    film: str
    quantity: int


def load_stock(path: Path) -> list[StockItem]:
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Не удалось прочитать запас пленки: {path}") from exc

    raw_items = data.get("items", [])
    if not isinstance(raw_items, list):
        raise ValueError(f"Неверный формат запаса пленки: {path}")

    items: list[StockItem] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            raise ValueError(f"Неверный формат запаса пленки: {path}")

        film = raw_item.get("film")
        quantity = raw_item.get("quantity")
        if not isinstance(film, str) or not film.strip() or not isinstance(quantity, int):
            raise ValueError(f"Неверный формат запаса пленки: {path}")
        if quantity <= 0:
            raise ValueError(f"Неверный формат запаса пленки: {path}")

        items.append(StockItem(film=film.strip(), quantity=quantity))

    return _sort_and_merge(items)


def save_stock(path: Path, items: list[StockItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _sort_and_merge(items)
    lines = []
    for item in normalized:
        lines.extend(
            [
                "[[items]]",
                f'film = "{item.film}"',
                f"quantity = {item.quantity}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def add_to_stock(items: list[StockItem], film: str, quantity: int) -> list[StockItem]:
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным.")

    merged = {item.film.casefold(): StockItem(item.film, item.quantity) for item in items}
    key = film.casefold()
    if key in merged:
        current = merged[key]
        merged[key] = StockItem(film=current.film, quantity=current.quantity + quantity)
    else:
        merged[key] = StockItem(film=film, quantity=quantity)
    return _sort_and_merge(list(merged.values()))


def remove_from_stock(items: list[StockItem], film: str, quantity: int) -> list[StockItem]:
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным.")

    updated: list[StockItem] = []
    removed = False
    for item in items:
        if item.film.casefold() != film.casefold():
            updated.append(item)
            continue

        if item.quantity < quantity:
            raise ValueError("В запасе недостаточно пленки.")

        removed = True
        remaining = item.quantity - quantity
        if remaining > 0:
            updated.append(StockItem(film=item.film, quantity=remaining))

    if not removed:
        raise ValueError("Такой пленки нет в запасе.")

    return _sort_and_merge(updated)


def _sort_and_merge(items: list[StockItem]) -> list[StockItem]:
    merged: dict[str, StockItem] = {}
    for item in items:
        key = item.film.casefold()
        if key in merged:
            current = merged[key]
            merged[key] = StockItem(film=current.film, quantity=current.quantity + item.quantity)
        else:
            merged[key] = item
    return sorted(merged.values(), key=lambda item: item.film.casefold())
