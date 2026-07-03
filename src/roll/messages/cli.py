class Message(str):
    def __new__(cls, key: str, text: str):
        obj = str.__new__(cls, text)
        obj.key = key
        return obj


class Headers:
    CONFIG_HEADER = Message("cli.config_header", "Конфигурация:")
    ARCHIVE_HEADER = Message("cli.archive_header", "Архив:")
    ARCHIVE_MISSING = Message("cli.archive_missing", "Архив не найден:")
    STATUS_HEADER = Message("cli.status_header", "Состояние индекса")
    STATUS_ARCHIVE_FOLDERS = Message("cli.status_archive_folders", "Папок в архиве:")
    STATUS_INDEXED = Message("cli.status_indexed", "Проиндексировано:")
    STATUS_UNINDEXED = Message("cli.status_unindexed", "Не проиндексировано:")
    STATUS_UNINDEXED_FOLDERS = Message("cli.status_unindexed_folders", "Не проиндексированные папки:")
    VOCAB_FILMS = Message("cli.vocab_films", "Пленки:")
    VOCAB_CAMERAS = Message("cli.vocab_cameras", "Камеры:")
    VOCAB_FEATURES = Message("cli.vocab_features", "Особенности:")
    VOCAB_KEYWORDS = Message("cli.vocab_keywords", "Ключевые слова:")


class Msg(Headers):
    CLI_UNINITIALIZED = Message("cli.uninitialized", "roll не инициализирован.")
    CLI_INITIALIZED = Message("cli.initialized", "roll инициализирован.")
    NO_RESULTS = Message("cli.no_results", "Ничего не найдено.")
    NO_STATS_DATA = Message("cli.no_stats_data", "Нет данных для статистики.")
    NO_ROLLS = Message("cli.no_rolls", "Нет роллов.")
    NO_LOADED_ROLLS = Message("cli.no_loaded_rolls", "Нет загруженных пленок.")
    STOCK_EMPTY = Message("cli.stock_empty", "Запас пуст.")
    STOCK_EMPTY_MANUAL = Message("cli.stock_empty_manual", "Запас пуст. Используй --manual для ручного ввода.")
    INVALID_DATE = Message("cli.invalid_date", "Неверная дата.")
    INVALID_QUANTITY = Message("cli.invalid_quantity", "Количество должно быть положительным.")
    ROLL_EXISTS = Message("cli.roll_exists", "Roll уже существует:")
    TAGS_NORMALIZED = Message("cli.tags_normalized", "Теги нормализованы.")
    TAGS_ALREADY_NORMALIZED = Message("cli.tags_already_normalized", "Теги уже нормализованы.")
    DOCTOR_FIX_HINT = Message("cli.doctor_fix_hint", "Запусти: rl doctor --fix")

    RUN_TO_INITIALIZE = Message("cli.run_to_initialize", "  rl init ~/your/archive/path")
    UNINITIALIZED_MESSAGE = Message("cli.uninitialized_message", "roll не инициализирован.\nЗапусти: rl init ~/your/archive/path")
    UNINITIALIZED_NOTICE = Message(
        "cli.uninitialized_notice",
        "\n".join(
            [
                str(CLI_UNINITIALIZED),
                "",
                "Запусти:",
                str(RUN_TO_INITIALIZE),
            ]
        ),
    )


RU = {value.key: str(value) for name, value in Msg.__dict__.items() if isinstance(value, Message)}
