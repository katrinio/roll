from pathlib import Path

import typer

from roll.config import Config, load_config
from roll.helpers.formatting import highlight_cli_names
from roll.messages import Msg


def require_config() -> Config:
    try:
        return load_config()
    except FileNotFoundError:
        typer.echo(highlight_cli_names(Msg.UNINITIALIZED_NOTICE))
        raise typer.Exit(code=1)


def require_directory(path: Path, message: str) -> Path:
    resolved_path = path.expanduser().resolve()

    if not resolved_path.exists() or not resolved_path.is_dir():
        typer.echo(f"{message} {resolved_path}")
        raise typer.Exit(code=1)

    return resolved_path


def require_archive(config: Config) -> Path:
    if not config.archives:
        typer.echo(highlight_cli_names(Msg.UNINITIALIZED_NOTICE))
        raise typer.Exit(code=1)
    return config.archives[0]
