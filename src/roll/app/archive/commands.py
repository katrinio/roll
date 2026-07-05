from __future__ import annotations

from roll.app.archive.search import search_rolls_by_filters
from roll.app.archive.search_output import render_search_results
from roll.app.archive.stats_output import render_stats_report
from roll.app.archive.status_output import render_status_report
from roll.app.diagnostics.doctor_output import render_doctor
from roll.app.workspace.vocabulary import archive_vocabulary
from roll.app.archive.selection import split_csv
from roll.filesystem import (
    build_archive_tree,
    count_photo_files,
    find_roll_folders,
    find_unindexed_folders,
)
from roll.helpers.output import echo_lines, echo_section
from roll.messages import Msg
from roll.helpers.guards import require_archive, require_config
import typer


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


def status() -> None:
    archive = require_archive(require_config())

    from roll.app.archive.search import find_rolls
    from roll.app.archive.stats import _count_statuses

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)
    rolls = find_rolls(archive)
    status_counts = _count_statuses(rolls)

    render_status_report(archive, roll_folders, unindexed_folders, status_counts)


def stats(year: str | None, verbose: bool) -> None:
    archive = require_archive(require_config())
    render_stats_report(archive, year, verbose)


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


def search(
    year: str | None = None,
    film: str | None = None,
    camera: str | None = None,
    status: str | None = None,
    query: str | None = None,
) -> None:
    if not any([year, film, camera, status, query]):
        typer.echo(str(Msg.SEARCH_NEEDS_QUERY_OR_FILTERS))
        raise typer.Exit(code=1)

    archive = require_archive(require_config())
    results = search_rolls_by_filters(
        [archive],
        year=year,
        films=split_csv(film),
        cameras=split_csv(camera),
        statuses=split_csv(status),
        query=query,
    )

    if not results:
        typer.echo(str(Msg.NO_RESULTS))
        return

    render_search_results(results)


def doctor(fix: bool, verbose: bool) -> None:
    if render_doctor(fix=fix, verbose=verbose):
        raise typer.Exit(code=1)
