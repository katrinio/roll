from pathlib import Path

import typer

from roll.config import CONFIG_DIR, CONFIG_FILE, load_config, save_config, Config
from roll.archive import find_roll_folders, find_unindexed_folders
from roll.formatting import highlight_cli_names
from roll.index import save_roll_index
from roll.messages import (
    ARCHIVE_HEADER,
    ARCHIVE_MISSING,
    CLI_INITIALIZED,
    CONFIG_HEADER,
    INDEX_DONE,
    SEARCH_NOT_IMPLEMENTED,
    STATUS_ARCHIVE_FOLDERS,
    STATUS_HEADER,
    STATUS_INDEXED,
    STATUS_UNINDEXED,
    STATUS_UNINDEXED_FOLDERS,
    UNINITIALIZED_NOTICE,
    VOCAB_CAMERAS,
    VOCAB_FEATURES,
    VOCAB_FILMS,
    VOCAB_KEYWORDS,
)
from roll.vocabulary import FILMS, CAMERAS, FEATURES, KEYWORDS

app = typer.Typer(help="Личный индекс пленок.")


def require_config():
    try:
        return load_config()
    except FileNotFoundError:
        typer.echo(highlight_cli_names(UNINITIALIZED_NOTICE))
        raise typer.Exit(code=1)


@app.command("init")
def init(
    archive: Path = typer.Argument(
        ...,
        help="Путь к архиву пленок.",
    ),
) -> None:
    """Инициализировать roll."""
    archive = archive.expanduser().resolve()

    if not archive.exists():
        typer.echo(f"Папка не найдена: {archive}")
        raise typer.Exit(code=1)

    if not archive.is_dir():
        typer.echo(f"Это не папка: {archive}")
        raise typer.Exit(code=1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    save_config(Config(archive=archive))

    typer.echo(highlight_cli_names(CLI_INITIALIZED))
    typer.echo(f"Archive: {archive}")
    typer.echo(f"Config:  {CONFIG_FILE}")

@app.command("search")
def search(query: str) -> None:
    """Искать пленку по ключевым словам."""
    typer.echo(f"{SEARCH_NOT_IMPLEMENTED} {query}")

@app.command("config")
def config() -> None:
    """Показать текущую конфигурацию."""
    config = require_config()

    typer.echo(CONFIG_HEADER)
    typer.echo("")
    typer.echo(f"{ARCHIVE_HEADER} {config.archive}")

@app.command("scan")
def scan() -> None:
    """Показать папки в архиве."""
    config = require_config()

    archive = config.archive

    if not archive.exists():
        typer.echo(f"{ARCHIVE_MISSING} {archive}")
        raise typer.Exit(code=1)

    typer.echo(ARCHIVE_HEADER)
    typer.echo(str(archive))
    typer.echo("")

    roll_folders = find_roll_folders(archive)

    typer.echo("Found roll folders:")

    for roll_dir in roll_folders:
        relative_path = roll_dir.relative_to(archive)
        typer.echo(f"- {relative_path}")

@app.command("status")
def status() -> None:
    """Показать состояние индекса."""
    config = require_config()
    archive = config.archive

    roll_folders = find_roll_folders(archive)
    unindexed_folders = find_unindexed_folders(archive)

    typer.echo(STATUS_HEADER)
    typer.echo("")
    typer.echo(f"{STATUS_ARCHIVE_FOLDERS} {len(roll_folders)}")
    typer.echo(f"{STATUS_INDEXED} {len(roll_folders) - len(unindexed_folders)}")
    typer.echo(f"{STATUS_UNINDEXED} {len(unindexed_folders)}")

    if unindexed_folders:
        typer.echo("")
        typer.echo(STATUS_UNINDEXED_FOLDERS)
        for folder in unindexed_folders:
            typer.echo(f"- {folder.relative_to(archive)}")


@app.command("index")
def index(
    folder: Path,
    film: str = typer.Option(..., prompt=True),
    features: str = typer.Option("", prompt=True),
    camera: str = typer.Option(..., prompt=True),
    loaded_at: str = typer.Option(..., prompt=True),
    keywords: str = typer.Option("", prompt=True),
) -> None:
    """Проиндексировать папку пленки."""
    folder = folder.expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        typer.echo(f"Папка не найдена: {folder}")
        raise typer.Exit(code=1)

    feature_list = [
        feature.strip().lower()
        for feature in features.split(",")
        if feature.strip()
    ]
    keyword_list = [
        keyword.strip().lower()
        for keyword in keywords.split(",")
        if keyword.strip()
    ]

    save_roll_index(
        folder=folder,
        film=film,
        features=feature_list,
        camera=camera,
        loaded_at=loaded_at,
        keywords=keyword_list,
    )

    typer.echo(INDEX_DONE)

@app.command("vocab")
def vocab() -> None:
    """Показать справочники."""
    typer.echo(VOCAB_FILMS)
    for film in FILMS:
        typer.echo(f"- {film}")

    typer.echo(f"\n{VOCAB_CAMERAS}")
    for camera in CAMERAS:
        typer.echo(f"- {camera}")

    typer.echo(f"\n{VOCAB_FEATURES}")
    for feature in FEATURES:
        typer.echo(f"- {feature}")

    typer.echo(f"\n{VOCAB_KEYWORDS}")
    for keyword in KEYWORDS:
        typer.echo(f"- {keyword}")
