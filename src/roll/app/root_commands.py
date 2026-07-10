from __future__ import annotations

from pathlib import Path

import typer

from roll.app.workspace.config import (
    CONFIG_DIR,
    CONFIG_FILE,
    Config,
    load_config,
    save_config,
    set_lang,
)
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_config, require_directory
from roll.helpers.output import echo_lines, echo_section
from roll.messages import Msg
from roll.version import get_latest_version, get_update_hint, get_version, is_outdated


def version() -> None:
    current = get_version()
    typer.echo(current)
    latest = get_latest_version()
    if latest and is_outdated(current=current, latest=latest):
        typer.echo(f"New version available: {latest}. {get_update_hint()}")
    raise typer.Exit()


def init(archive: Path) -> None:
    archive = require_directory(archive, Msg.ARCHIVE_MISSING)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = load_config()
        archives = list(dict.fromkeys([*config.archives, archive]))
    except FileNotFoundError:
        archives = [archive]
    save_config(Config(archives=archives))

    from roll.app.workspace.workspace import workspace_for

    workspace_for(archive).ensure_structure()

    typer.echo(highlight_cli_names(Msg.CLI_INITIALIZED))
    echo_lines([f"Archive: {archive}", f"Config:  {CONFIG_FILE}"])


def update() -> None:
    typer.echo(str(Msg.UPDATE_USE_PACKAGE_MANAGER))
    raise typer.Exit(code=1)


def config() -> None:
    config = require_config()
    echo_section(
        Msg.CONFIG_HEADER,
        [f"{Msg.ARCHIVE_HEADER} {archive}" for archive in config.archives],
    )


def config_lang(lang: str | None) -> None:
    config = require_config()

    if lang is None:
        typer.echo(f"{Msg.LANGUAGE} {config.lang}")
        return

    normalized = lang.upper()
    if normalized not in {"EN", "RU"}:
        typer.echo(str(Msg.ALLOWED_VALUES))
        raise typer.Exit(code=1)

    updated = set_lang(normalized)
    typer.echo(f"{Msg.LANGUAGE_SET_TO} {updated.lang}")
