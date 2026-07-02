import typer


def choose_from_list(label: str, options: list[str]) -> str:
    typer.echo("")
    typer.echo(label)
    for index, option in enumerate(options, start=1):
        typer.echo(f"{index}. {option}")
    value = typer.prompt("Выбери номер")

    try:
        selected_index = int(value)
    except ValueError:
        typer.echo("Нужно ввести номер.")
        raise typer.Exit(code=1)

    if selected_index < 1 or selected_index > len(options):
        typer.echo("Такого номера нет.")
        raise typer.Exit(code=1)
    return options[selected_index - 1]
