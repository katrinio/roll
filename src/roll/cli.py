from pathlib import Path

import typer
import yaml

from roll.config import CONFIG_DIR, CONFIG_FILE, load_config, save_config, Config
from roll.formatting import highlight_command_names

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

    typer.echo("roll initialized")
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
        typer.echo(highlight_command_names("roll не инициализирован."))
        typer.echo("")
        typer.echo("Запусти:")
        typer.echo(highlight_command_names("  rl init ~/Pictures/plenka"))
        raise typer.Exit(code=1)

    typer.echo("Configuration")
    typer.echo("")
    typer.echo(f"Archive: {config.archive}")
