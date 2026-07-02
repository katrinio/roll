from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Личный индекс пленок.")


CONFIG_DIR = Path.home() / ".config" / "roll"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


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

    config = {
        "archive": str(archive),
    }

    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, allow_unicode=True, sort_keys=False)

    typer.echo("roll initialized")
    typer.echo(f"Archive: {archive}")
    typer.echo(f"Config:  {CONFIG_FILE}")

@app.command("search")
def search(query: str) -> None:
    """Искать пленку по ключевым словам."""
    typer.echo(f"Search is not implemented yet: {query}")