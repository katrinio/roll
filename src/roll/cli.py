from pathlib import Path

import typer

from roll.archive import find_roll_folders, find_unindexed_folders
from roll.app.config import CONFIG_DIR, CONFIG_FILE, Config, load_config, save_config
from roll.app.diagnostics import run_doctor
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_archive, require_config, require_directory
from roll.helpers.output import echo_lines, echo_list, echo_section
from roll.helpers.parsing import parse_csv
from roll.app.index import save_roll_index
from roll.messages import Msg
from roll.app.normalization import (
    apply_normalization_plans,
    build_normalization_plan,
    print_normalization_plan,
)
from roll.app.search import search_rolls
from roll.app.vocabulary import archive_vocabulary
from roll.app.workspace import workspace_for

app = typer.Typer(help="Личный индекс пленок.")


@app.command("init")
def init(archive: Path = typer.Argument(..., help="Путь к архиву пленок.")) -> None:
    """Инициализировать roll."""
    archive = require_directory(archive, "Папка не найдена:")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = load_config()
        archives = list(dict.fromkeys([*config.archives, archive]))
    except FileNotFoundError:
        archives = [archive]
    save_config(Config(archives=archives))

    workspace = workspace_for(archive)
    workspace.ensure_structure()

    typer.echo(highlight_cli_names(Msg.CLI_INITIALIZED))
    echo_lines([f"Archive: {archive}", f"Config:  {CONFIG_FILE}"])


@app.command("config")
def config() -> None:
    """Показать текущую конфигурацию."""
    config = require_config()
    echo_section(Msg.CONFIG_HEADER, [f"{Msg.ARCHIVE_HEADER} {archive}" for archive in config.archives])


@app.command("scan")
def scan() -> None:
    """Показать папки в архиве."""
    archive = require_archive(require_config())

    if not archive.exists():
        typer.echo(f"{Msg.ARCHIVE_MISSING} {archive}")
        raise typer.Exit(code=1)

    echo_section(Msg.ARCHIVE_HEADER, [str(archive)])

    roll_folders = find_roll_folders(archive)
    typer.echo("Found roll folders:")
    echo_list((roll_dir.relative_to(archive) for roll_dir in roll_folders))


@app.command("status")
def status() -> None:
    """Показать состояние индекса."""
    archive = require_archive(require_config())

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)

    echo_lines(
        [
            Msg.STATUS_HEADER,
            "",
            f"{Msg.STATUS_ARCHIVE_FOLDERS} {len(roll_folders)}",
            f"{Msg.STATUS_INDEXED} {len(roll_folders) - len(unindexed_folders)}",
            f"{Msg.STATUS_UNINDEXED} {len(unindexed_folders)}",
        ]
    )

    if unindexed_folders:
        echo_lines(["", Msg.STATUS_UNINDEXED_FOLDERS])
        echo_list((folder.relative_to(archive) for folder in unindexed_folders))


@app.command("index")
def index(
    folder: Path,
    film: str = typer.Option("", prompt=True),
    features: str = typer.Option(""),
    camera: str = typer.Option("", prompt=True),
    loaded_at: str = typer.Option(..., prompt=True),
    keywords: str = typer.Option(""),
) -> None:
    """Проиндексировать папку пленки."""
    folder = require_directory(folder, "Папка не найдена:")
    save_roll_index(
        folder=folder,
        archive=folder.parents[1],
        film=film,
        features=parse_csv(features),
        camera=camera,
        loaded_at=loaded_at,
        keywords=parse_csv(keywords),
    )

    typer.echo(Msg.INDEX_DONE)


@app.command("vocab")
def vocab() -> None:
    """Показать справочники."""
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
def search(query: str) -> None:
    """Искать пленки по памяти."""
    archive = require_archive(require_config())
    results = search_rolls(archive, query)

    if not results:
        typer.echo("Ничего не найдено.")
        return

    echo_lines(["Найдено:", ""])

    for roll in results:
        echo_lines([f"{roll.loaded_at} — {roll.film}", f"Камера: {roll.camera}"])

        if roll.features:
            typer.echo(f"Особенности: {', '.join(roll.features)}")

        if roll.keywords:
            typer.echo(f"Ключевые слова: {', '.join(roll.keywords)}")

        echo_lines([f"Папка: {roll.folder}", ""])


@app.command("doctor")
def doctor() -> None:
    """Проверить целостность архива и конфигурации."""
    try:
        config = load_config()
    except FileNotFoundError:
        report = run_doctor(Config(archives=[]))
    else:
        report = run_doctor(config)

    if not report.issues:
        typer.echo(Msg.DOCTOR_OK)
        return

    echo_lines(
        [
            highlight_cli_names(
                f"{Msg.DOCTOR_ERROR_PREFIX if issue.level == 'error' else Msg.DOCTOR_WARN_PREFIX} {issue.message}"
            )
            for issue in report.issues
        ]
    )

    if report.has_errors:
        raise typer.Exit(code=1)


@app.command("normalize")
def normalize() -> None:
    """Привести архив к единому виду."""
    config = require_config()
    plans = [build_normalization_plan(archive) for archive in config.archives]

    total_rules = sum(len(plan.rules) for plan in plans)
    has_changes = any(plan.has_changes for plan in plans)

    for plan in plans:
        echo_lines([f"{Msg.ARCHIVE_HEADER} {plan.archive}", *print_normalization_plan(plan), ""])

    if not has_changes:
        return

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
        echo_lines(["Обнаружены конфликты:"])
        echo_list(all_conflicts)
        raise typer.Exit(code=1)

    if not typer.confirm(f"Переименовать {total_rules} папок?", default=False):
        return

    apply_normalization_plans(plans)
