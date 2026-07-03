from pathlib import Path

import typer

from roll.filesystem import build_archive_tree, count_photo_files, find_roll_folders, find_unindexed_folders
from roll.app.workspace.config import CONFIG_DIR, CONFIG_FILE, Config, load_config, save_config
from roll.app.archive.batch import process_archives
from roll.app.workspace.roll_store import load_roll_metadata, update_roll_features, update_roll_keywords
from roll.app.archive.normalization import (
    apply_normalization_plans,
    build_normalization_plan,
    normalize_keywords_in_archive,
)
from roll.helpers.autocomplete import autocomplete_many_prompt, choice_prompt
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_archive, require_config, require_directory
from roll.helpers.output import echo_lines, echo_section
from roll.app.flows.stock import app as stock_app
from roll.app.flows.stock import load as load_roll
from roll.messages import Msg
from roll.app.archive.status_output import render_status_report
from roll.app.archive.search import find_rolls, search_rolls
from roll.app.archive.search_output import render_search_results
from roll.app.archive.normalization_output import render_normalization_plans
from roll.app.archive.stats import _count_statuses
from roll.app.archive.stats_output import render_stats_report
from roll.app.workspace.vocabulary import archive_vocabulary
from roll.app.workspace.workspace import workspace_for
from roll.app.diagnostics.doctor_output import render_doctor

app = typer.Typer(help="Личный индекс пленок.")
app.add_typer(stock_app, name="stock")


tags_app = typer.Typer(help="Теги роллов.")
app.add_typer(tags_app, name="tags")

features_app = typer.Typer(help="Особенности роллов.")
app.add_typer(features_app, name="features")

batch_app = typer.Typer(help="Пакетные операции.")
app.add_typer(batch_app, name="batch")


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
    tree = build_archive_tree(archive)
    photo_count = sum(count_photo_files(folder) for folder in roll_folders)

    if tree:
        typer.echo("Дерево архива:")
        echo_lines(tree)
        typer.echo("")

    typer.echo(f"Папок: {len(roll_folders)}")
    typer.echo(f"Фото: {photo_count}")


@app.command("status")
def status() -> None:
    """Показать состояние индекса."""
    archive = require_archive(require_config())

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)
    rolls = find_rolls(archive)
    status_counts = _count_statuses(rolls)

    render_status_report(archive, roll_folders, unindexed_folders, status_counts)


@app.command("stats")
def stats(
    year: str | None = typer.Argument(None, help="Год для фильтрации статистики."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Показать полный список значений."),
) -> None:
    """Показать статистику по архиву."""
    archive = require_archive(require_config())
    render_stats_report(archive, year, verbose)


@app.command("load")
def load(manual: bool = typer.Option(False, "--manual", help="Вводить пленку вручную через справочник.")) -> None:
    """Загрузить пленку из запаса в новый roll."""
    load_roll(manual=manual)


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
def search(query: str | None = typer.Argument(None, help="Строка для поиска по памяти.")) -> None:
    """Искать пленки по памяти."""
    if not query:
        typer.echo("Нужно указать строку поиска. Пример: rl search pizza")
        raise typer.Exit(code=1)

    archive = require_archive(require_config())
    results = search_rolls(archive, query)

    if not results:
        typer.echo(Msg.NO_RESULTS)
        return

    render_search_results(results)


@app.command("doctor")
def doctor(
    fix: bool = typer.Option(False, "--fix", help="Применить безопасные исправления."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Показать полный список безопасных исправлений."),
) -> None:
    """Проверить целостность архива и конфигурации."""
    if render_doctor(fix=fix, verbose=verbose):
        raise typer.Exit(code=1)


@tags_app.command("add")
def add_tags() -> None:
    _update_roll_list_field("Теги", "keywords", update_roll_keywords, "Теги обновлены")


@features_app.command("add")
def add_features() -> None:
    _update_roll_list_field("Особенности", "features", update_roll_features, "Особенности обновлены")


def _update_roll_list_field(
    prompt_title: str,
    dictionary_name: str,
    updater,
    success_label: str,
) -> None:
    archive = require_archive(require_config())
    rolls = [folder for folder in find_roll_folders(archive) if (folder / "roll.toml").exists()]

    if not rolls:
        typer.echo(Msg.NO_ROLLS)
        raise typer.Exit(code=1)

    selected = _choose_roll_folder(rolls)
    workspace = workspace_for(archive)
    values = autocomplete_many_prompt(prompt_title, workspace.dictionary(dictionary_name))
    try:
        metadata = updater(selected / "roll.toml", values)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{success_label}: {metadata.film}")


@batch_app.command("process")
def batch_process() -> None:
    config = require_config()
    process_archives(config.archives)


@app.command("normalize")
def normalize(
    tags: bool = typer.Option(False, "--tags", help="Нормализовать теги в uppercase."),
) -> None:
    """Привести архив к единому виду."""
    config = require_config()

    if tags:
        touched = []
        for archive in config.archives:
            touched.extend(normalize_keywords_in_archive(archive))
        if touched:
            typer.echo(Msg.TAGS_NORMALIZED)
            for path in touched:
                typer.echo(f"  {path}")
        else:
            typer.echo(Msg.TAGS_ALREADY_NORMALIZED)
        return

    plans = [build_normalization_plan(archive) for archive in config.archives]
    total_rules, has_changes = render_normalization_plans(plans)
    if not has_changes:
        return

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
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
