class Headers:
    CONFIG_HEADER = "Конфигурация:"
    ARCHIVE_HEADER = "Архив:"
    ARCHIVE_MISSING = "Архив не найден:"
    STATUS_HEADER = "Состояние индекса"
    STATUS_ARCHIVE_FOLDERS = "Папок в архиве:"
    STATUS_INDEXED = "Проиндексировано:"
    STATUS_UNINDEXED = "Не проиндексировано:"
    STATUS_UNINDEXED_FOLDERS = "Не проиндексированные папки:"
    VOCAB_FILMS = "Пленки:"
    VOCAB_CAMERAS = "Камеры:"
    VOCAB_FEATURES = "Особенности:"
    VOCAB_KEYWORDS = "Ключевые слова:"


class Msg(Headers):
    CLI_UNINITIALIZED = "roll не инициализирован."
    CLI_INITIALIZED = "roll инициализирован."
    NO_RESULTS = "Ничего не найдено."
    NO_STATS_DATA = "Нет данных для статистики."
    NO_ROLLS = "Нет роллов."
    NO_LOADED_ROLLS = "Нет загруженных пленок."
    STOCK_EMPTY = "Запас пуст."
    STOCK_EMPTY_MANUAL = "Запас пуст. Используй --manual для ручного ввода."
    INVALID_DATE = "Неверная дата."
    INVALID_QUANTITY = "Количество должно быть положительным."
    ROLL_EXISTS = "Roll уже существует:"
    TAGS_NORMALIZED = "Теги нормализованы."
    TAGS_ALREADY_NORMALIZED = "Теги уже нормализованы."
    DOCTOR_FIX_HINT = "Запусти: rl doctor --fix"

    RUN_TO_INITIALIZE = "  rl init ~/your/archive/path"
    UNINITIALIZED_MESSAGE = "roll не инициализирован.\nЗапусти: rl init ~/your/archive/path"
    UNINITIALIZED_NOTICE = "\n".join(
        [
            CLI_UNINITIALIZED,
            "",
            "Запусти:",
            RUN_TO_INITIALIZE,
        ]
    )

