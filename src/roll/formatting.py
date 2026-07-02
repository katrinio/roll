import click


def highlight_cli_names(message: str) -> str:
    return (
        message.replace("roll", click.style("roll", fg="cyan"))
        .replace("rl", click.style("rl", fg="cyan"))
    )
