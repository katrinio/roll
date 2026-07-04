from roll.messages.cli import Message


class Normalize:
    HEADER = Message("normalize.header", "Нормализация архива", "Archive normalization")
    ALREADY_NORMALIZED = Message("normalize.already_normalized", "Архив уже нормализован.", "Archive is already normalized.")
    QUESTION = Message("normalize.question", "Переименовать {count} папок?", "Rename {count} folders?")
    CONFLICTS_HEADER = Message("normalize.conflicts_header", "Обнаружены конфликты:", "Conflicts detected:")


RU = {value.key: str(value) for name, value in Normalize.__dict__.items() if isinstance(value, Message)}
