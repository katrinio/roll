class Headers:
    CONFIG_HEADER = "Конфигурация:"
    ARCHIVE_HEADER = "Архив:"
    ARCHIVE_MISSING = "Архив не найден:"
    SEARCH_NOT_IMPLEMENTED = "Поиск пока не реализован:"
    INDEX_DONE = "Пленка проиндексирована."
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

class Doctor:
    OK = "OK"
    ERROR_PREFIX = "ERROR:"
    WARN_PREFIX = "WARN:"
    NO_ARCHIVES = "В глобальной конфигурации нет архивов."
    ARCHIVE_MISSING = "Архив не найден:"
    WORKSPACE_MISSING = "Нет папки .roll:"
    VOCAB_DIR_MISSING = "Нет папки словарей:"
    VOCAB_FILE_MISSING = "Нет файла словаря:"
    ROLL_MISSING = "Нет файла roll.toml:"
    ROLL_UNREADABLE = "Не удалось прочитать roll.toml:"
    REQUIRED_FIELD_MISSING = "Нет обязательного поля"
    FILM_NOT_IN_VOCAB = "Пленка не в словаре:"
    CAMERA_NOT_IN_VOCAB = "Камера не в словаре:"
    FEATURE_NOT_IN_VOCAB = "Особенность не в словаре:"
    KEYWORD_NOT_IN_VOCAB = "Ключевое слово не в словаре:"
    UNINDEXED_FOLDERS = "Не проиндексировано папок:"
    SUSPICIOUS_YEAR = "Подозрительное имя года:"
    SUSPICIOUS_ROLL = "Подозрительное имя папки:"
