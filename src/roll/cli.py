from pathlib import Path

import typer

from roll.archive import find_roll_folders, find_unindexed_folders
from roll.app.config import CONFIG_DIR, CONFIG_FILE, Config, load_config, save_config
from roll.app.diagnostics import Doctor, run_doctor
from roll.app.roll_store import load_roll_metadata, update_roll_keywords
from roll.helpers.autocomplete import autocomplete_many_prompt, choice_prompt
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_archive, require_config, require_directory
from roll.helpers.output import echo_lines, echo_list, echo_section
from roll.app.stock import app as stock_app
from roll.app.stock import load as load_roll
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
app.add_typer(stock_app, name="stock")


tags_app = typer.Typer(help="Теги роллов.")
app.add_typer(tags_app, name="tags")


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


@app.command("load")
def load() -> None:
    """Загрузить пленку из запаса в новый roll."""
    load_roll()


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
            typer.echo(f"Теги: {', '.join(roll.keywords)}")

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
        typer.echo(Doctor.OK)
        return

    echo_lines(
        [
            highlight_cli_names(
                f"{Doctor.ERROR_PREFIX if issue.level == 'error' else Doctor.WARN_PREFIX} {issue.message}"
            )
            for issue in report.issues
        ]
    )

    if report.has_errors:
        raise typer.Exit(code=1)


@tags_app.command("add")
def add_tags() -> None:
    archive = require_archive(require_config())
    rolls = [folder for folder in find_roll_folders(archive) if (folder / "roll.toml").exists()]

    if not rolls:
        typer.echo("Нет роллов.")
        raise typer.Exit(code=1)

    selected = _choose_roll_folder(rolls)
    workspace = workspace_for(archive)
    tags = autocomplete_many_prompt("Теги", workspace.dictionary("keywords"))
    try:
        metadata = update_roll_keywords(selected / "roll.toml", tags)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"Теги обновлены: {metadata.film}")


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


def _choose_roll_folder(rolls: list[Path]) -> Path:
    labels = [f"{str(path.relative_to(path.parents[1]))} ({_roll_status(path)})" for path in rolls]
    selected_label = choice_prompt("Roll", labels)
    for path in rolls:
        label = f"{str(path.relative_to(path.parents[1]))} ({_roll_status(path)})"
        if label == selected_label:
            return path
    raise ValueError("Не удалось выбрать roll.")


def _roll_status(path: Path) -> str:
    try:
        return load_roll_metadata(path / "roll.toml").status
    except ValueError:
        return "unknown"
