
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

from roll.dictionaries import Dictionary


def autocomplete_prompt(title: str, dictionary: Dictionary) -> str:
    while True:
        value = prompt(f"{title}: ", completer=_completer(dictionary), complete_while_typing=True).strip()

        if not value:
            continue

        existing = _existing_value(dictionary, value)
        if existing is not None:
            return existing

        if _confirm_missing(value):
            return dictionary.add(value)


def autocomplete_many_prompt(title: str, dictionary: Dictionary) -> list[str]:
    while True:
        value = prompt(f"{title}: ", completer=_completer(dictionary), complete_while_typing=True).strip()

        if not value:
            continue

        resolved = _resolve_many(dictionary, value)
        if resolved is not None:
            return resolved


def choice_prompt(title: str, choices: list[str]) -> str:
    if not choices:
        raise ValueError("No choices available.")

    while True:
        value = prompt(f"{title}: ", completer=_choice_completer(choices), complete_while_typing=True).strip()
        if not value:
            continue

        existing = _existing_choice(choices, value)
        if existing is not None:
            return existing


def _completer(dictionary: Dictionary) -> FuzzyCompleter:
    return FuzzyCompleter(
        WordCompleter(dictionary.read(), ignore_case=True, sentence=True, match_middle=True)
    )


def _existing_value(dictionary: Dictionary, candidate: str) -> str | None:
    for value in dictionary.read():
        if value.casefold() == candidate.casefold():
            return value
    return None


def _confirm_missing(value: str) -> bool:
    answer = prompt(f"'{value}' отсутствует в словаре.\n\nДобавить? [Y/n] ").strip().casefold()
    return answer in ("", "y", "yes", "д", "да")


def _choice_completer(choices: list[str]) -> FuzzyCompleter:
    return FuzzyCompleter(WordCompleter(choices, ignore_case=True, sentence=True, match_middle=True))


def _existing_choice(choices: list[str], candidate: str) -> str | None:
    for value in choices:
        if value.casefold() == candidate.casefold():
            return value
    return None


def _resolve_many(dictionary: Dictionary, value: str) -> list[str] | None:
    selected: list[str] = []
    for token in [item.strip() for item in value.split(",") if item.strip()]:
        existing = _existing_value(dictionary, token)
        if existing is not None:
            resolved = existing
        elif _confirm_missing(token):
            resolved = dictionary.add(token)
        else:
            return None

        if resolved not in selected:
            selected.append(resolved)

    return selected
