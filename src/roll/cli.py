from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import typer

from roll.app.archive.commands import (
    doctor as archive_doctor,
    scan as archive_scan,
    search as archive_search,
    stats as archive_stats,
    status as archive_status,
    vocab as archive_vocab,
)
from roll.app.flows.stock import app as stock_app
from roll.app.flows.stock import edit_batch, edit_list_field, load as load_roll
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
from roll.messages import Msg, Normalize
from roll.version import get_latest_version, get_version, is_outdated

app = typer.Typer(help=Msg.CLI_INITIALIZED)
app.add_typer(stock_app, name="stock")

config_app = typer.Typer(help=Msg.CONFIG_HEADER)
app.add_typer(config_app, name="config")

tags_app = typer.Typer(help=Msg.VOCAB_KEYWORDS)
app.add_typer(tags_app, name="tags")

features_app = typer.Typer(help=Msg.VOCAB_FEATURES)
app.add_typer(features_app, name="features")

batch_app = typer.Typer(help=Msg.BATCH_WILL_PROCESS)
app.add_typer(batch_app, name="batch")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", help="Show version and exit.", is_eager=True
    ),
) -> None:
    if version:
        current = get_version()
        typer.echo(current)
        latest = get_latest_version()
        if latest and is_outdated(current=current, latest=latest):
            typer.echo(f"New version available: {latest}. Run `rl update`.")
        raise typer.Exit()
    if ctx.invoked_subcommand is not None:
        return


@app.command("init")
def init(archive: Path = typer.Argument(..., help=Msg.ARCHIVE_HEADER)) -> None:
    archive = require_directory(archive, Msg.ARCHIVE_MISSING)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = load_config()
        archives = list(dict.fromkeys([*config.archives, archive]))
    except FileNotFoundError:
        archives = [archive]
    save_config(Config(archives=archives))

    workspace = archive  # preserved for behavior-free local setup
    from roll.app.workspace.workspace import workspace_for

    workspace_for(workspace).ensure_structure()

    typer.echo(highlight_cli_names(Msg.CLI_INITIALIZED))
    echo_lines([f"Archive: {archive}", f"Config:  {CONFIG_FILE}"])


@app.command("update")
def update() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-input",
            "--upgrade",
            "--force-reinstall",
            "git+https://github.com/katrinio/roll.git@main",
        ],
        check=False,
    )
    raise typer.Exit(code=result.returncode)


@config_app.callback(invoke_without_command=True)
def config(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    config = require_config()
    echo_section(
        Msg.CONFIG_HEADER,
        [f"{Msg.ARCHIVE_HEADER} {archive}" for archive in config.archives],
    )


@config_app.command("lang")
def config_lang(lang: str | None = typer.Argument(None, help=Msg.LANGUAGE)) -> None:
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


@app.command("scan")
def scan() -> None:
    archive_scan()


@app.command("status")
def status() -> None:
    archive_status()


@app.command("stats")
def stats(
    year: str | None = typer.Argument(None, help=Msg.STATS_YEAR),
    verbose: bool = typer.Option(False, "-v", "--verbose", help=Msg.STATS_MORE),
) -> None:
    archive_stats(year, verbose)


@app.command("load")
def load(
    manual: bool = typer.Option(False, "--manual", help=Msg.STOCK_EMPTY_MANUAL),
) -> None:
    load_roll(manual=manual)


@app.command("vocab")
def vocab() -> None:
    archive_vocab()


@app.command("search")
def search(
    year: str | None = typer.Option(None, "--year", help=Msg.BATCH_FILTER_YEAR),
    film: str | None = typer.Option(None, "--film", help=Msg.BATCH_FILTER_FILM),
    camera: str | None = typer.Option(None, "--camera", help=Msg.BATCH_FILTER_CAMERA),
    status: str | None = typer.Option(None, "--status", help=Msg.BATCH_FILTER_STATUS),
    query: str | None = typer.Argument(None, help=Msg.SEARCH_QUERY_REQUIRED),
) -> None:
    archive_search(year, film, camera, status, query)


@app.command("doctor")
def doctor(
    fix: bool = typer.Option(False, "--fix", help=Msg.DOCTOR_CAN_FIX),
    verbose: bool = typer.Option(False, "-v", "--verbose", help=Msg.DOCTOR_CAN_ADD),
) -> None:
    archive_doctor(fix, verbose)


@tags_app.command("add")
def add_tags() -> None:
    edit_list_field("Tags", "keywords", "Tags updated")


@features_app.command("add")
def add_features() -> None:
    edit_list_field("Features", "features", "Features updated")


@batch_app.callback(invoke_without_command=True)
def batch(
    ctx: typer.Context,
    year: str | None = typer.Option(None, "--year", help=Msg.BATCH_FILTER_YEAR),
    film: str | None = typer.Option(None, "--film", help=Msg.BATCH_FILTER_FILM),
    camera: str | None = typer.Option(None, "--camera", help=Msg.BATCH_FILTER_CAMERA),
    status: str | None = typer.Option(None, "--status", help=Msg.BATCH_FILTER_STATUS),
    set_status: str | None = typer.Option(
        None, "--set-status", help=Msg.BATCH_SET_STATUS
    ),
    set_camera: str | None = typer.Option(
        None, "--set-camera", help=Msg.BATCH_SET_CAMERA
    ),
    add_feature: str | None = typer.Option(
        None, "--add-feature", help=Msg.BATCH_ADD_FEATURE
    ),
    add_tag: str | None = typer.Option(None, "--add-tag", help=Msg.BATCH_ADD_TAG),
) -> None:
    if ctx.invoked_subcommand is not None:
        return

    edit_batch(year, film, camera, status, set_status, set_camera, add_feature, add_tag)


@app.command("normalize")
def normalize(
    tags: bool = typer.Option(False, "--tags", help=Msg.TAGS_NORMALIZED),
    photos: bool = typer.Option(False, "--photos", help=Normalize.HEADER),
) -> None:
    from roll.app.archive.normalize_commands import normalize as normalize_command

    normalize_command(tags, photos)
