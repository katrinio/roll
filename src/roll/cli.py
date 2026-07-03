from pathlib import Path

import typer

from roll.archive import build_archive_tree, count_photo_files, find_roll_folders, find_unindexed_folders
from roll.app.config import CONFIG_DIR, CONFIG_FILE, Config, load_config, save_config
from roll.app.diagnostics import Doctor, run_doctor
from roll.app.roll_store import load_roll_metadata, update_roll_features, update_roll_keywords
from roll.app.normalization import (
    apply_normalization_plans,
    apply_keyword_vocab_fixes,
    build_normalization_plan,
    build_safe_rename_plan,
    collect_keyword_vocab_fixes,
    normalize_keywords_in_archive,
    print_normalization_plan,
)
from roll.helpers.autocomplete import autocomplete_many_prompt, choice_prompt
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_archive, require_config, require_directory
from roll.helpers.output import echo_lines, echo_list, echo_section
from roll.app.stock import app as stock_app
from roll.app.stock import load as load_roll
from roll.messages import Msg
from roll.app.search import search_rolls
from roll.app.search import find_rolls
from roll.app.vocabulary import archive_vocabulary
from roll.app.workspace import workspace_for

app = typer.Typer(help="Личный индекс пленок.")
app.add_typer(stock_app, name="stock")


tags_app = typer.Typer(help="Теги роллов.")
app.add_typer(tags_app, name="tags")

features_app = typer.Typer(help="Особенности роллов.")
app.add_typer(features_app, name="features")


DOCTOR_MESSAGE_PREFIXES = (
    Msg.ARCHIVE_MISSING,
    Doctor.WORKSPACE_CONFIG_MISSING,
    Doctor.WORKSPACE_CONFIG_MISMATCH,
    Doctor.WORKSPACE_MISSING,
    Doctor.VOCAB_DIR_MISSING,
    Doctor.VOCAB_FILE_MISSING,
    Doctor.ROLL_UNREADABLE,
    Doctor.REQUIRED_FIELD_MISSING,
    Doctor.FILM_NOT_IN_VOCAB,
    Doctor.CAMERA_NOT_IN_VOCAB,
    Doctor.FEATURE_NOT_IN_VOCAB,
    Doctor.KEYWORD_NOT_IN_VOCAB,
    Doctor.KEYWORD_NOT_NORMALIZED,
    Doctor.SUSPICIOUS_YEAR,
    Doctor.SUSPICIOUS_ROLL,
)


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
    status_counts = _count_roll_statuses(rolls)

    echo_lines(
        [
            Msg.STATUS_HEADER,
            "",
            f"{Msg.STATUS_ARCHIVE_FOLDERS} {len(roll_folders)}",
            f"{Msg.STATUS_INDEXED} {len(roll_folders) - len(unindexed_folders)}",
            f"{Msg.STATUS_UNINDEXED} {len(unindexed_folders)}",
            "",
            "Пленки по статусам:",
            f"loaded: {status_counts.get('loaded', 0)}",
            f"processed: {status_counts.get('processed', 0)}",
            f"failed: {status_counts.get('failed', 0)}",
            f"без roll.toml: {len(unindexed_folders)}",
        ]
    )

    if unindexed_folders:
        echo_lines(["", Msg.STATUS_UNINDEXED_FOLDERS])
        echo_list((folder.relative_to(archive) for folder in unindexed_folders))


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
        typer.echo("Нужно указать строку поиска. Пример: rl search kir")
        raise typer.Exit(code=1)

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
def doctor(
    fix: bool = typer.Option(False, "--fix", help="Применить безопасные исправления."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Показать полный список безопасных исправлений."),
) -> None:
    """Проверить целостность архива и конфигурации."""
    try:
        config = load_config()
    except FileNotFoundError:
        report = run_doctor(Config(archives=[]))
    else:
        report = run_doctor(config)

    if not report.issues and not report.missing_rolls:
        typer.echo(Doctor.OK)
        return

    error_groups: dict[str, list[str]] = {}
    warning_groups: dict[str, list[str]] = {}
    error_order: list[str] = []
    warning_order: list[str] = []

    if report.missing_rolls:
        _append_doctor_group(
            error_groups,
            error_order,
            Doctor.ROLL_MISSING,
            [str(path) for path in report.missing_rolls],
        )

    for issue in report.issues:
        title, item = _split_doctor_message(issue.message)
        if issue.level == "error":
            _append_doctor_group(error_groups, error_order, title, [item])
        else:
            _append_doctor_group(warning_groups, warning_order, title, [item])

    if error_order:
        _echo_doctor_block(Doctor.ERROR_PREFIX, error_order, error_groups)
    if warning_order:
        if error_order:
            typer.echo("")
        _echo_doctor_block(Doctor.WARN_PREFIX, warning_order, warning_groups)

    if report.fixable:
        echo_lines([""])
        typer.echo(highlight_cli_names(f"Можно исправить: {len(report.fixable)}"))
        items = report.fixable if verbose else report.fixable[:5]
        echo_lines([f"  {item}" for item in items])
        if not verbose and len(report.fixable) > 5:
            typer.echo(f"  ... и еще {len(report.fixable) - 5}")
        if fix:
            plans = [build_safe_rename_plan(archive) for archive in config.archives]
            apply_normalization_plans(plans)
            typer.echo("Исправления применены.")
            if verbose:
                for plan in plans:
                    if plan.rules:
                        echo_lines([""])
                        echo_lines(print_normalization_plan(plan))

    if report.keyword_vocab_fixes:
        echo_lines([""])
        typer.echo(highlight_cli_names(f"Можно добавить в keywords: {len(report.keyword_vocab_fixes)}"))
        items = report.keyword_vocab_fixes if verbose else report.keyword_vocab_fixes[:5]
        echo_lines([f"  {item}" for item in items])
        if not verbose and len(report.keyword_vocab_fixes) > 5:
            typer.echo(f"  ... и еще {len(report.keyword_vocab_fixes) - 5}")
        if fix:
            for archive in config.archives:
                applied = apply_keyword_vocab_fixes(archive, collect_keyword_vocab_fixes(archive))
                if applied and verbose:
                    echo_lines([""])
                    typer.echo(f"  {applied}")
            typer.echo("Исправления keywords применены.")
        else:
            typer.echo("")
            typer.echo("Запусти: rl doctor --fix")

    if error_order:
        raise typer.Exit(code=1)


def _append_doctor_group(
    groups: dict[str, list[str]],
    order: list[str],
    title: str,
    items: list[str],
) -> None:
    if title not in groups:
        groups[title] = []
        order.append(title)
    groups[title].extend(items)


def _split_doctor_message(message: str) -> tuple[str, str]:
    for prefix in DOCTOR_MESSAGE_PREFIXES:
        if message.startswith(prefix):
            item = message.removeprefix(prefix).strip()
            return prefix, item
    return message, message


def _echo_doctor_block(prefix: str, order: list[str], groups: dict[str, list[str]]) -> None:
    total = sum(len(groups[title]) for title in order)
    typer.echo(highlight_cli_names(f"{prefix} {total}"))
    for title in order:
        items = groups[title]
        typer.echo(f"  {_doctor_group_title(title)} {len(items)}")
        echo_lines([f"    {item}" for item in items])


def _doctor_group_title(title: str) -> str:
    return title if title.endswith(":") else f"{title}:"


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


@features_app.command("add")
def add_features() -> None:
    archive = require_archive(require_config())
    rolls = [folder for folder in find_roll_folders(archive) if (folder / "roll.toml").exists()]

    if not rolls:
        typer.echo("Нет роллов.")
        raise typer.Exit(code=1)

    selected = _choose_roll_folder(rolls)
    workspace = workspace_for(archive)
    features = autocomplete_many_prompt("Особенности", workspace.dictionary("features"))
    try:
        metadata = update_roll_features(selected / "roll.toml", features)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"Особенности обновлены: {metadata.film}")


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
            typer.echo("Теги нормализованы.")
            for path in touched:
                typer.echo(f"  {path}")
        else:
            typer.echo("Теги уже нормализованы.")
        return

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


def _count_roll_statuses(rolls) -> dict[str, int]:
    counts = {"loaded": 0, "processed": 0, "failed": 0}
    for roll in rolls:
        if roll.status in counts:
            counts[roll.status] += 1
    return counts
