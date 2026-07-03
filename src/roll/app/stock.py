from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

import typer

from roll.app.workspace import workspace_for
from roll.helpers.autocomplete import autocomplete_prompt
from roll.helpers.guards import require_archive, require_config
from roll.helpers.output import echo_lines


@dataclass(frozen=True)
class StockItem:
    film: str
    quantity: int


app = typer.Typer(help="Запас пленки.")


@app.command("add")
def add() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    film = autocomplete_prompt("Пленка", workspace.dictionary("films"))
    quantity = typer.prompt("Количество:", type=int)
    if quantity <= 0:
        typer.echo("Количество должно быть положительным.")
        raise typer.Exit(code=1)

    try:
        items = load_stock(workspace.stock_file)
        updated = add_to_stock(items, film, quantity)
        save_stock(workspace.stock_file, updated)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)


@app.command("list")
def list_stock() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)
    try:
        items = load_stock(workspace.stock_file)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    if not items:
        typer.echo("Запас пуст.")
        return

    echo_lines(["Запас пленки"])
    for item in items:
        typer.echo(f"{item.film:<20} ×{item.quantity}")


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
