
from roll.messages.cli import detect_locale

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
            return []

        resolved = _resolve_many(dictionary, value)
        if resolved is not None:
            return resolved


def choice_prompt(title: str, choices: list[str]) -> str:
    if not choices:
        raise ValueError("No choices available." if detect_locale() == "en" else "Нет доступных вариантов.")

    while True:
        value = prompt(f"{title}: ", completer=_choice_completer(choices), complete_while_typing=True).strip()
        if not value:
            continue

        matched = _match_choice(choices, value)
        if matched is not None:
            return matched


def _completer(dictionary: Dictionary, exclude: list[str] | None = None) -> FuzzyCompleter:
    excluded = {value.casefold() for value in (exclude or [])}
    choices = [value for value in dictionary.read() if value.casefold() not in excluded]
    return FuzzyCompleter(WordCompleter(choices, ignore_case=True, sentence=True, match_middle=True))


def _resolve_many(dictionary: Dictionary, value: str) -> list[str] | None:
    selected: list[str] = []
    for token in [item.strip() for item in value.split(",") if item.strip()]:
        existing = _existing_value(dictionary, token)
        if existing is None:
            if not _confirm_missing(token):
                return None
            existing = dictionary.add(token)

        if existing not in selected:
            selected.append(existing)

    return selected


def _existing_value(dictionary: Dictionary, candidate: str) -> str | None:
    for value in dictionary.read():
        if value.casefold() == candidate.casefold():
            return value
    return None


def _confirm_missing(value: str) -> bool:
    question = f"'{value}' отсутствует в словаре.\n\nДобавить? [Y/n] " if detect_locale() != "en" else f"'{value}' is missing from the dictionary.\n\nAdd it? [Y/n] "
    answer = prompt(question).strip().casefold()
    return answer in ("", "y", "yes", "д", "да")


def _choice_completer(choices: list[str]) -> FuzzyCompleter:
    return FuzzyCompleter(WordCompleter(choices, ignore_case=True, sentence=True, match_middle=True))


def _match_choice(choices: list[str], candidate: str) -> str | None:
    normalized = _normalize_choice(candidate)
    matches = [value for value in choices if _normalize_choice(value) == normalized]

    if len(matches) == 1:
        return matches[0]

    substring_matches = [value for value in choices if normalized in _normalize_choice(value)]

    if len(substring_matches) == 1:
        return substring_matches[0]

    prefix_matches = [value for value in choices if _normalize_choice(value).startswith(normalized)]
    if len(prefix_matches) == 1:
        return prefix_matches[0]

    return None


def _normalize_choice(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())
