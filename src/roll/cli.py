from pathlib import Path

import typer

from roll.archive import find_roll_folders, find_unindexed_folders
from roll.config import CONFIG_DIR, CONFIG_FILE, Config, save_config
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.guards import require_config, require_directory
from roll.helpers.parsing import parse_csv
from roll.index import save_roll_index
from roll.messages import Msg
from roll.vocabulary import CAMERAS, FEATURES, FILMS, KEYWORDS

app = typer.Typer(help="Личный индекс пленок.")


@app.command("init")
def init(archive: Path = typer.Argument(..., help="Путь к архиву пленок.")) -> None:
    """Инициализировать roll."""
    archive = require_directory(archive, "Папка не найдена:")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    save_config(Config(archive=archive))

    typer.echo(highlight_cli_names(Msg.CLI_INITIALIZED))
    typer.echo(f"Archive: {archive}")
    typer.echo(f"Config:  {CONFIG_FILE}")


@app.command("search")
def search(query: str) -> None:
    """Искать пленку по ключевым словам."""
    typer.echo(f"{Msg.SEARCH_NOT_IMPLEMENTED} {query}")


@app.command("config")
def config() -> None:
    """Показать текущую конфигурацию."""
    config = require_config()
    typer.echo(Msg.CONFIG_HEADER)
    typer.echo("")
    typer.echo(f"{Msg.ARCHIVE_HEADER} {config.archive}")


@app.command("scan")
def scan() -> None:
    """Показать папки в архиве."""
    config = require_config()
    archive = config.archive

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
    config = require_config()
    archive = config.archive

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
    typer.echo(Msg.VOCAB_FILMS)
    for film in FILMS.read():
        typer.echo(f"- {film}")

    typer.echo(f"\n{Msg.VOCAB_CAMERAS}")
    for camera in CAMERAS.read():
        typer.echo(f"- {camera}")

    typer.echo(f"\n{Msg.VOCAB_FEATURES}")
    for feature in FEATURES.read():
        typer.echo(f"- {feature}")

    typer.echo(f"\n{Msg.VOCAB_KEYWORDS}")
    for keyword in KEYWORDS.read():
        typer.echo(f"- {keyword}")
