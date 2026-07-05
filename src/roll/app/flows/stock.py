from __future__ import annotations

import typer

from roll.messages import Msg
from roll.app.flows.stock_edit import (
    edit as _edit,
    edit_batch as _edit_batch,
    edit_list_field as _edit_list_field,
)
from roll.app.flows.stock_lifecycle import (
    add as _add,
    load as _load,
    list_stock as _list_stock,
    process as _process,
)

app = typer.Typer(help=Msg.STOCK_HEADER)


@app.command("add")
def add() -> None:
    _add()


@app.command("load")
def load(
    manual: bool = typer.Option(
        False, "--manual", help="Enter film manually from dictionary."
    ),
) -> None:
    _load(manual)


@app.command("process")
def process() -> None:
    _process("processed", "Processed")


@app.command("failed")
def failed() -> None:
    _process("failed", "Marked as failed")


@app.command("list")
def list_stock() -> None:
    _list_stock()


def edit() -> None:
    _edit()


def edit_list_field(
    prompt_title: str, dictionary_name: str, success_label: str
) -> None:
    _edit_list_field(prompt_title, dictionary_name, success_label)


def edit_batch(
    year: str | None,
    film: str | None,
    camera: str | None,
    status: str | None,
    set_status: str | None,
    set_camera: str | None,
    add_feature: str | None,
    add_tag: str | None,
) -> None:
    _edit_batch(
        year, film, camera, status, set_status, set_camera, add_feature, add_tag
    )


def _rolls(archive):
    from roll.app.flows.stock_edit import _rolls as stock_edit_rolls

    return stock_edit_rolls(archive)


def _format_roll_label(path):
    from roll.app.flows.stock_edit import (
        _format_roll_label as stock_edit_format_roll_label,
    )

    return stock_edit_format_roll_label(path)


def _prompt_roll_metadata(archive, roll_file, metadata):
    from roll.app.flows.stock_edit import (
        _prompt_roll_metadata as stock_edit_prompt_roll_metadata,
    )

    return stock_edit_prompt_roll_metadata(archive, roll_file, metadata)
