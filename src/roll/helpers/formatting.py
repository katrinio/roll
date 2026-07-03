import click


def highlight_cli_names(message: str) -> str:
    return (
        message.replace("ERROR:", click.style("ERROR:", fg="red", bold=True))
        .replace("WARN:", click.style("WARN:", fg="yellow", bold=True))
        .replace("roll", click.style("roll", fg="cyan"))
        .replace("rl", click.style("rl", fg="cyan"))
    )
