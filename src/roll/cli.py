from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import typer

from roll.app.archive.normalize_cli import (
    build_photo_normalization_plans as _build_photo_normalization_plans_impl,
    echo_photo_plan_preview as _echo_photo_plan_preview_impl,
)
from roll.app.archive.normalization import (
    apply_normalization_plans,
    build_normalization_plan,
    normalize_keywords_in_archive,
)
from roll.app.archive.photo_dates import guess_archive_year
from roll.app.archive.normalization_output import render_normalization_plans
from roll.app.archive.search import search_rolls
from roll.app.archive.search_output import render_search_results
from roll.app.archive.stats_output import render_stats_report
from roll.app.archive.status_output import render_status_report
from roll.app.diagnostics.doctor_output import render_doctor
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
from roll.app.workspace.vocabulary import archive_vocabulary
from roll.filesystem import (
    build_archive_tree,
    count_photo_files,
    find_roll_folders,
    find_unindexed_folders,
)
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import (
    require_archive,
    require_config,
    require_current_archive,
    require_directory,
)
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
    archive = require_archive(require_config())

    if not archive.exists():
        typer.echo(f"{Msg.ARCHIVE_MISSING} {archive}")
        raise typer.Exit(code=1)

    echo_section(Msg.ARCHIVE_HEADER, [str(archive)])
    roll_folders = find_roll_folders(archive)
    tree = build_archive_tree(archive)
    photo_count = sum(count_photo_files(folder) for folder in roll_folders)

    if tree:
        typer.echo(str(Msg.TREE_HEADER))
        echo_lines(tree)
        typer.echo("")

    typer.echo(f"{Msg.FOLDERS} {len(roll_folders)}")
    typer.echo(f"{Msg.FILES} {photo_count}")


@app.command("status")
def status() -> None:
    archive = require_archive(require_config())

    from roll.app.archive.search import find_rolls
    from roll.app.archive.stats import _count_statuses

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)
    rolls = find_rolls(archive)
    status_counts = _count_statuses(rolls)

    render_status_report(archive, roll_folders, unindexed_folders, status_counts)


@app.command("stats")
def stats(
    year: str | None = typer.Argument(None, help=Msg.STATS_YEAR),
    verbose: bool = typer.Option(False, "-v", "--verbose", help=Msg.STATS_MORE),
) -> None:
    archive = require_archive(require_config())
    render_stats_report(archive, year, verbose)


@app.command("load")
def load(
    manual: bool = typer.Option(False, "--manual", help=Msg.STOCK_EMPTY_MANUAL),
) -> None:
    load_roll(manual=manual)


@app.command("vocab")
def vocab() -> None:
    archive = require_archive(require_config())
    vocab = archive_vocabulary(archive)

    for title, items in (
        (Msg.VOCAB_FILMS, vocab["films"].read()),
        (Msg.VOCAB_CAMERAS, vocab["cameras"].read()),
        (Msg.VOCAB_FEATURES, vocab["features"].read()),
        (Msg.VOCAB_KEYWORDS, vocab["keywords"].read()),
    ):
        echo_section(title, [f"- {item}" for item in items])


@app.command("search")
def search(
    query: str | None = typer.Argument(None, help=Msg.SEARCH_QUERY_REQUIRED),
) -> None:
    if not query:
        typer.echo(str(Msg.SEARCH_QUERY_REQUIRED))
        raise typer.Exit(code=1)

    archive = require_archive(require_config())
    results = search_rolls(archive, query)

    if not results:
        typer.echo(str(Msg.NO_RESULTS))
        return

    render_search_results(results)


@app.command("doctor")
def doctor(
    fix: bool = typer.Option(False, "--fix", help=Msg.DOCTOR_CAN_FIX),
    verbose: bool = typer.Option(False, "-v", "--verbose", help=Msg.DOCTOR_CAN_ADD),
) -> None:
    if render_doctor(fix=fix, verbose=verbose):
        raise typer.Exit(code=1)


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
    config = require_config()
    archive = require_current_archive(config)

    if tags:
        touched = normalize_keywords_in_archive(archive)
        if touched:
            typer.echo(str(Msg.TAGS_NORMALIZED))
            for path in touched:
                typer.echo(f"  {path}")
        else:
            typer.echo(str(Msg.TAGS_ALREADY_NORMALIZED))
        return

    if photos:
        plans = _build_photo_normalization_plans_impl(archive)
        total_rules, has_changes = render_normalization_plans(plans)
        if not has_changes:
            return

        all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
        if all_conflicts:
            raise typer.Exit(code=1)

        _echo_photo_plan_preview_impl(plans)
        if not typer.confirm(
            str(Normalize.QUESTION).format(count=total_rules), default=False
        ):
            return

        apply_normalization_plans(plans)
        return

    plans = [build_normalization_plan(archive)]
    total_rules, has_changes = render_normalization_plans(plans)
    if not has_changes:
        return

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
        raise typer.Exit(code=1)

    if not typer.confirm(
        str(Normalize.QUESTION).format(count=total_rules), default=False
    ):
        return

    apply_normalization_plans(plans)


def _build_photo_normalization_plans(archive: Path):
    folders = _photo_folders(archive)
    year = guess_archive_year(archive)
    if year is None:
        typer.echo(str(Msg.CLI_UNINITIALIZED))
        raise typer.Exit(code=1)

    if not typer.confirm(
        str(Msg.NORMALIZE_PHOTOS_CONFIRM_YEAR).format(year=year), default=True
    ):
        typed_year = typer.prompt(
            str(Msg.NORMALIZE_PHOTOS_YEAR).format(folder=archive.name)
        )
        year = _parse_year(typed_year)

    manual_months = len(folders) > 1 and typer.confirm(
        str(Msg.NORMALIZE_PHOTOS_MANUAL), default=False
    )
    return [
        _build_photo_plan_for_folder(folder, archive, year, manual_months)
        for folder in folders
    ]


def _photo_folders(archive: Path) -> list[Path]:
    return [
        path for path in archive.iterdir() if path.is_dir() and path.name != ".roll"
    ]


def _build_photo_plan_for_folder(
    folder: Path, archive: Path, year: int, manual_months: bool
):
    from roll.app.archive.normalization import NormalizationPlan, RenameRule

    month = _prompt_month(folder) if manual_months else _guess_month(folder)

    if month is None:
        return NormalizationPlan(archive=archive, rules=[], conflicts=[])

    target = archive / f"{year:04d}" / f"{month:02d}-01"
    if target.exists():
        return NormalizationPlan(
            archive=archive,
            rules=[],
            conflicts=[f"{Msg.NORMALIZE_PHOTOS_MONTH} {target}"],
        )

    return NormalizationPlan(
        archive=archive, rules=[RenameRule(folder=folder, target=target)], conflicts=[]
    )


def _prompt_month(folder: Path) -> int:
    while True:
        value = typer.prompt(
            str(Msg.NORMALIZE_PHOTOS_MONTH).format(folder=folder.name)
        ).strip()
        month = _parse_month(value)
        if month is not None:
            return month


def _guess_month(folder: Path) -> int | None:
    from roll.app.archive.photo_dates import guess_archive_month

    guess = guess_archive_month(folder)
    return guess.month if guess is not None else None


def _parse_year(value: str) -> int:
    year = value.strip()
    if len(year) == 4 and year.isdigit():
        return int(year)
    raise typer.Exit(code=1)


def _parse_month(value: str) -> int | None:
    month = value.strip()
    if len(month) == 2 and month.isdigit() and 1 <= int(month) <= 12:
        return int(month)
    return None
