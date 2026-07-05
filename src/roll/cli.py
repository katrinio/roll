from __future__ import annotations

from pathlib import Path

import typer

from roll.app.archive.commands import (
    doctor as archive_doctor,
    scan as archive_scan,
    search as archive_search,
    stats as archive_stats,
    status as archive_status,
    vocab as archive_vocab,
)
from roll.app.archive.batch import process_archives
from roll.app.root_commands import config as root_config
from roll.app.root_commands import config_lang as root_config_lang
from roll.app.root_commands import init as root_init
from roll.app.root_commands import update as root_update
from roll.app.root_commands import version as root_version
from roll.app.flows.stock import app as stock_app
from roll.app.flows.stock import edit_batch, edit_list_field, load as load_roll
from roll.helpers.guards import require_config
from roll.messages import Msg, Normalize

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
        root_version()
    if ctx.invoked_subcommand is not None:
        return


@app.command("init")
def init(archive: Path = typer.Argument(..., help=Msg.ARCHIVE_HEADER)) -> None:
    root_init(archive)


@app.command("update")
def update() -> None:
    root_update()


@config_app.callback(invoke_without_command=True)
def config(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    root_config()


@config_app.command("lang")
def config_lang(lang: str | None = typer.Argument(None, help=Msg.LANGUAGE)) -> None:
    root_config_lang(lang)


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


@batch_app.command("process")
def batch_process() -> None:
    process_archives(require_config().archives)


@app.command("normalize")
def normalize(
    tags: bool = typer.Option(False, "--tags", help=Msg.TAGS_NORMALIZED),
    photos: bool = typer.Option(False, "--photos", help=Normalize.HEADER),
) -> None:
    from roll.app.archive.normalize_commands import normalize as normalize_command

    normalize_command(tags, photos)
