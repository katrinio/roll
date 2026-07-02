import typer

from roll.dictionaries import Dictionary


def choose_or_create(dictionary: Dictionary, label: str) -> str:
    options = dictionary.read()

    if options:
        typer.echo("")
        typer.echo(label)
        for index, option in enumerate(options, start=1):
            typer.echo(f"{index}. {option}")
        typer.echo("0. Ввести новую")
        value = typer.prompt("Выбери номер")

        if value == "0":
            return _prompt_and_add(dictionary)

        try:
            selected_index = int(value)
        except ValueError:
            typer.echo("Нужно ввести номер.")
            raise typer.Exit(code=1)

        if selected_index < 1 or selected_index > len(options):
            typer.echo("Такого номера нет.")
            raise typer.Exit(code=1)
        return options[selected_index - 1]

    return _prompt_and_add(dictionary)


def choose_many(dictionary: Dictionary, label: str, prompt: str) -> list[str]:
    options = dictionary.read()

    if options:
        typer.echo("")
        typer.echo(label)
        for index, option in enumerate(options, start=1):
            typer.echo(f"{index}. {option}")
        typer.echo(prompt)
        value = typer.prompt(">")
    else:
        value = typer.prompt(prompt)

    selected: list[str] = []
    for token in [item.strip() for item in value.split(",") if item.strip()]:
        if token == "0":
            created = _prompt_and_add(dictionary)
            if created not in selected:
                selected.append(created)
            continue

        if token.isdigit():
            index = int(token)
            if index < 1 or index > len(options):
                typer.echo("Такого номера нет.")
                raise typer.Exit(code=1)
            value = options[index - 1]
        else:
            value = dictionary.add(token)

        if value not in selected:
            selected.append(value)

    return selected


def _prompt_and_add(dictionary: Dictionary) -> str:
    value = typer.prompt("Введи новое значение").strip()
    if not value:
        typer.echo("Нужно ввести значение.")
        raise typer.Exit(code=1)
    return dictionary.add(value)
