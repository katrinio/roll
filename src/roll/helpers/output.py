from collections.abc import Iterable

import typer


def echo_lines(lines: Iterable[str]) -> None:
    for line in lines:
        typer.echo(line)


def echo_section(title: str, body: Iterable[str] = ()) -> None:
    typer.echo(title)
    typer.echo("")
    echo_lines(body)


def echo_list(items: Iterable[str], prefix: str = "- ") -> None:
    echo_lines(f"{prefix}{item}" for item in items)
