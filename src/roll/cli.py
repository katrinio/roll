from pathlib import Path

import typer
import yaml

from roll.config import CONFIG_DIR, CONFIG_FILE, load_config, save_config, Config
from roll.formatting import highlight_cli_names
from roll.messages import (
    ARCHIVE_HEADER,
    ARCHIVE_MISSING,
    CLI_INITIALIZED,
    CONFIG_HEADER,
    UNINITIALIZED_NOTICE,
)

app = typer.Typer(help="Личный индекс пленок.")


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
    typer.echo(f"Search is not implemented yet: {query}")

@app.command("config")
def config() -> None:
    """Показать текущую конфигурацию."""
    try:
        config = load_config()
    except FileNotFoundError:
        typer.echo(highlight_cli_names(UNINITIALIZED_NOTICE))
        raise typer.Exit(code=1)

    typer.echo(CONFIG_HEADER)
    typer.echo("")
    typer.echo(f"{ARCHIVE_HEADER} {config.archive}")

@app.command("scan")
def scan() -> None:
    """Показать папки в архиве."""
    try:
        config = load_config()
    except FileNotFoundError:
        typer.echo(highlight_cli_names(UNINITIALIZED_NOTICE))
        raise typer.Exit(code=1)

    archive = config.archive

    if not archive.exists():
        typer.echo(f"{ARCHIVE_MISSING} {archive}")
        raise typer.Exit(code=1)

    typer.echo(ARCHIVE_HEADER)
    typer.echo(str(archive))
    typer.echo("")

    year_dirs = sorted(path for path in archive.iterdir() if path.is_dir())

    typer.echo("Found years:")
    for year_dir in year_dirs:
        typer.echo(f"- {year_dir.name}")

    typer.echo("")
    typer.echo("Found roll folders:")

    for year_dir in year_dirs:
        roll_dirs = sorted(path for path in year_dir.iterdir() if path.is_dir())

        for roll_dir in roll_dirs:
            relative_path = roll_dir.relative_to(archive)
            typer.echo(f"- {relative_path}")
