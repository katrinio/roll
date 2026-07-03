from roll.messages.cli import Message


class Normalize:
    HEADER = Message("normalize.header", "Нормализация архива")
    ALREADY_NORMALIZED = Message("normalize.already_normalized", "Архив уже нормализован.")
    QUESTION = Message("normalize.question", "Переименовать {count} папок?")
    CONFLICTS_HEADER = Message("normalize.conflicts_header", "Обнаружены конфликты:")


RU = {value.key: str(value) for name, value in Normalize.__dict__.items() if isinstance(value, Message)}
