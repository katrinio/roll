from roll.messages.cli import Message


class Normalize:
    HEADER = Message("normalize.header", "Нормализация архива", "Archive normalization")
    ALREADY_NORMALIZED = Message(
        "normalize.already_normalized",
        "Архив уже нормализован.",
        "Archive already normalized.",
    )
    QUESTION = Message(
        "normalize.question", "Переименовать {count} папок?", "Rename {count} folders?"
    )
    CONFLICTS_HEADER = Message("normalize.conflicts_header", "Конфликты:", "Conflicts:")
    TARGET_ALREADY_EXISTS = Message(
        "normalize.target_already_exists",
        "Целевая папка уже существует:",
        "Target already exists:",
    )
    TARGET_COLLIDES_WITH_SOURCE = Message(
        "normalize.target_collides_with_source",
        "Цель совпадает с источником:",
        "Target matches source:",
    )
    DUPLICATE_TARGET = Message(
        "normalize.duplicate_target", "Дублирующаяся цель:", "Duplicate target:"
    )


RU = {
    value.key: str(value)
    for name, value in Normalize.__dict__.items()
    if isinstance(value, Message)
}
