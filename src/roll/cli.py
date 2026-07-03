from pathlib import Path

import typer

from roll.archive import find_roll_folders, find_unindexed_folders
from roll.config import CONFIG_DIR, CONFIG_FILE, Config, load_config, save_config
from roll.diagnostics import run_doctor
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_archive, require_config, require_directory
from roll.helpers.parsing import parse_csv
from roll.index import save_roll_index
from roll.messages import Msg
from roll.normalization import (
    apply_normalization_plan,
    build_normalization_plan,
    print_normalization_plan,
)
from roll.search import search_rolls
from roll.vocabulary import archive_vocabulary
from roll.workspace import workspace_for

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
    typer.echo(f"Archive: {archive}")
    typer.echo(f"Config:  {CONFIG_FILE}")


@app.command("config")
def config() -> None:
    """Показать текущую конфигурацию."""
    config = require_config()
    typer.echo(Msg.CONFIG_HEADER)
    typer.echo("")
    for archive in config.archives:
        typer.echo(f"{Msg.ARCHIVE_HEADER} {archive}")


@app.command("scan")
def scan() -> None:
    """Показать папки в архиве."""
    archive = require_archive(require_config())

    if not archive.exists():
        typer.echo(f"{Msg.ARCHIVE_MISSING} {archive}")
        raise typer.Exit(code=1)

    typer.echo(Msg.ARCHIVE_HEADER)
    typer.echo(str(archive))
    typer.echo("")

    roll_folders = find_roll_folders(archive)
    typer.echo("Found roll folders:")
    for roll_dir in roll_folders:
        typer.echo(f"- {roll_dir.relative_to(archive)}")


@app.command("status")
def status() -> None:
    """Показать состояние индекса."""
    archive = require_archive(require_config())

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)

    typer.echo(Msg.STATUS_HEADER)
    typer.echo("")
    typer.echo(f"{Msg.STATUS_ARCHIVE_FOLDERS} {len(roll_folders)}")
    typer.echo(f"{Msg.STATUS_INDEXED} {len(roll_folders) - len(unindexed_folders)}")
    typer.echo(f"{Msg.STATUS_UNINDEXED} {len(unindexed_folders)}")

    if unindexed_folders:
        typer.echo("")
        typer.echo(Msg.STATUS_UNINDEXED_FOLDERS)
        for folder in unindexed_folders:
            typer.echo(f"- {folder.relative_to(archive)}")


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

    typer.echo(Msg.VOCAB_FILMS)
    for film in vocab["films"].read():
        typer.echo(f"- {film}")

    typer.echo(f"\n{Msg.VOCAB_CAMERAS}")
    for camera in vocab["cameras"].read():
        typer.echo(f"- {camera}")

    typer.echo(f"\n{Msg.VOCAB_FEATURES}")
    for feature in vocab["features"].read():
        typer.echo(f"- {feature}")

    typer.echo(f"\n{Msg.VOCAB_KEYWORDS}")
    for keyword in vocab["keywords"].read():
        typer.echo(f"- {keyword}")


@app.command("search")
def search(query: str) -> None:
    """Искать пленки по памяти."""
    archive = require_archive(require_config())
    results = search_rolls(archive, query)

    if not results:
        typer.echo("Ничего не найдено.")
        return

    typer.echo("Найдено:")
    typer.echo("")

    for roll in results:
        typer.echo(f"{roll.loaded_at} — {roll.film}")
        typer.echo(f"Камера: {roll.camera}")

        if roll.features:
            typer.echo(f"Особенности: {', '.join(roll.features)}")

        if roll.keywords:
            typer.echo(f"Ключевые слова: {', '.join(roll.keywords)}")

        typer.echo(f"Папка: {roll.folder}")
        typer.echo("")


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

    for issue in report.issues:
        prefix = Msg.DOCTOR_ERROR_PREFIX if issue.level == "error" else Msg.DOCTOR_WARN_PREFIX
        typer.echo(highlight_cli_names(f"{prefix} {issue.message}"))

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
        typer.echo(f"{Msg.ARCHIVE_HEADER} {plan.archive}")
        for line in print_normalization_plan(plan):
            typer.echo(line)
        typer.echo("")

    if not has_changes:
        return

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
        typer.echo("Обнаружены конфликты:")
        for conflict in all_conflicts:
            typer.echo(f"- {conflict}")
        raise typer.Exit(code=1)

    if not typer.confirm(f"Переименовать {total_rules} папок?", default=False):
        return

    for plan in plans:
        apply_normalization_plan(plan)
