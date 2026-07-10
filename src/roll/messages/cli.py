from __future__ import annotations

import tomllib
from pathlib import Path


def detect_locale() -> str:
    config_lang = _load_lang_from_config_file()
    if config_lang in {"EN", "RU"}:
        return config_lang.lower()
    return "en"


def _load_lang_from_config_file() -> str | None:
    config_file = Path.home() / ".config" / "roll" / "config.toml"
    if not config_file.exists():
        return None

    try:
        data = tomllib.loads(config_file.read_text(encoding="utf-8"))
    except Exception:
        return None

    value = data.get("lang")
    return str(value).upper() if isinstance(value, str) else None


class Message(str):
    def __new__(cls, key: str, ru: str, en: str | None = None):
        obj = str.__new__(cls, ru)
        obj.key = key
        obj.ru = ru
        obj.en = en or ru
        return obj

    def _value(self) -> str:
        return self.en if detect_locale() == "en" and self.en is not None else self.ru

    def __str__(self) -> str:
        return self._value()

    def __repr__(self) -> str:
        return repr(self._value())

    def __format__(self, format_spec: str) -> str:
        return format(self._value(), format_spec)


class Headers:
    CONFIG_HEADER = Message("cli.config_header", "Конфигурация:", "Configuration:")
    ARCHIVE_HEADER = Message("cli.archive_header", "Архив:", "Archive:")
    ARCHIVE_MISSING = Message(
        "cli.archive_missing", "Архив не найден:", "Archive not found:"
    )
    STATUS_HEADER = Message("cli.status_header", "Состояние", "Status")
    STATUS_ARCHIVE_FOLDERS = Message(
        "cli.status_archive_folders", "Папок в архиве:", "Folders in archive:"
    )
    STATUS_INDEXED = Message("cli.status_indexed", "Проиндексировано:", "Indexed:")
    STATUS_UNINDEXED = Message(
        "cli.status_unindexed", "Не проиндексировано:", "Not indexed:"
    )
    STATUS_UNINDEXED_FOLDERS = Message(
        "cli.status_unindexed_folders",
        "Не проиндексированные папки:",
        "Unindexed folders:",
    )
    STATUS_ROLLS = Message("cli.status_rolls", "По статусам:", "By status:")
    STATUS_NO_ROLL_TOML = Message(
        "cli.status_no_roll_toml", "без roll.toml:", "without roll.toml:"
    )
    TREE_HEADER = Message("cli.tree_header", "Дерево архива:", "Archive tree:")
    FILES = Message("cli.files", "Фото:", "Photos:")
    FOLDERS = Message("cli.folders", "Папок:", "Folders:")
    SEARCH_HEADER = Message("cli.search_header", "Найдено:", "Found:")
    SEARCH_CAMERA = Message("cli.search_camera", "Камера:", "Camera:")
    SEARCH_FEATURES = Message("cli.search_features", "Особенности:", "Features:")
    SEARCH_TAGS = Message("cli.search_tags", "Теги:", "Tags:")
    SEARCH_FOLDER = Message("cli.search_folder", "Папка:", "Folder:")
    VOCAB_FILMS = Message("cli.vocab_films", "Пленки:", "Films:")
    VOCAB_CAMERAS = Message("cli.vocab_cameras", "Камеры:", "Cameras:")
    VOCAB_FEATURES = Message("cli.vocab_features", "Особенности:", "Features:")
    VOCAB_KEYWORDS = Message("cli.vocab_keywords", "Ключевые слова:", "Keywords:")


class Msg(Headers):
    CLI_UNINITIALIZED = Message(
        "cli.uninitialized", "Архив не инициализирован.", "Archive not initialized."
    )
    CLI_INITIALIZED = Message(
        "cli.initialized", "Инициализация завершена.", "Initialized."
    )
    NO_RESULTS = Message("cli.no_results", "Ничего не найдено.", "Nothing found.")
    NO_STATS_DATA = Message(
        "cli.no_stats_data", "Нет данных для статистики.", "No statistics data."
    )
    NO_ROLLS = Message("cli.no_rolls", "Нет роллов.", "No rolls.")
    NO_LOADED_ROLLS = Message(
        "cli.no_loaded_rolls", "Нет загруженных пленок.", "No loaded films."
    )
    STOCK_EMPTY = Message("cli.stock_empty", "Запас пуст.", "Stock is empty.")
    STOCK_HEADER = Message("cli.stock_header", "Запас", "Stock")
    STOCK_EMPTY_MANUAL = Message(
        "cli.stock_empty_manual",
        "Запас пуст. Используй --manual.",
        "Stock is empty. Use --manual.",
    )
    ROLL_EDIT_HEADER = Message("cli.roll_edit_header", "Редактирование", "Editing")
    ROLL_EDIT_SELECT = Message("cli.roll_edit_select", "Выберите ролл", "Select roll")
    ROLL_EDIT_AVAILABLE = Message(
        "cli.roll_edit_available", "Доступные роллы:", "Available rolls:"
    )
    ROLL_EDIT_FILM = Message("cli.roll_edit_film", "Пленка", "Film")
    ROLL_EDIT_CAMERA = Message("cli.roll_edit_camera", "Камера", "Camera")
    ROLL_EDIT_STATUS = Message("cli.roll_edit_status", "Статус", "Status")
    ROLL_EDIT_FEATURES = Message("cli.roll_edit_features", "Особенности", "Features")
    ROLL_EDIT_KEYWORDS = Message("cli.roll_edit_keywords", "Ключевые слова", "Keywords")
    ROLL_EDIT_ROLL_LABEL = Message(
        "cli.roll_edit_roll_label",
        "{path} | {film} | {camera} | {status}",
        "{path} | {film} | {camera} | {status}",
    )
    ROLL_EDIT_ORIGINAL_SOURCE = Message(
        "cli.roll_edit_original_source", "Исходник", "Original source"
    )
    ROLL_EDIT_DIGITAL_COPY = Message(
        "cli.roll_edit_digital_copy", "Цифровая копия", "Digital copy"
    )
    ROLL_EDIT_ORIGINAL_STATUS = Message(
        "cli.roll_edit_original_status", "Состояние оригинала", "Original status"
    )
    ROLL_EDIT_SELECT_HINT = Message(
        "cli.roll_edit_select_hint", "Номер или Enter", "Number or Enter"
    )
    ROLL_EDIT_UPDATED = Message("cli.roll_edit_updated", "Обновлено.", "Updated.")
    PROMPT_QUANTITY = Message("cli.prompt_quantity", "Количество:", "Quantity:")
    PROMPT_FILM = Message("cli.prompt_film", "Пленка:", "Film:")
    PROMPT_CAMERA = Message("cli.prompt_camera", "Камера:", "Camera:")
    PROMPT_LOAD_DATE = Message("cli.prompt_load_date", "Дата загрузки", "Load date")
    PROMPT_MANUAL_FILM = Message("cli.prompt_manual_film", "Пленка: ", "Film: ")
    LOAD_SUCCESS = Message("cli.load_success", "Загружено:", "Loaded:")
    PROCESS_SUCCESS = Message("cli.process_success", "Обработано:", "Processed:")
    FAILED_SUCCESS = Message(
        "cli.failed_success", "Помечено как failed:", "Marked as failed:"
    )
    INVALID_DATE = Message("cli.invalid_date", "Неверная дата.", "Invalid date.")
    INVALID_QUANTITY = Message(
        "cli.invalid_quantity",
        "Количество должно быть положительным.",
        "Quantity must be positive.",
    )
    ROLL_EXISTS = Message(
        "cli.roll_exists", "Roll уже существует:", "Roll already exists:"
    )
    CHOOSE_STOCK = Message("cli.choose_stock", "Выберите пленку.", "Select film.")
    SEARCH_QUERY_REQUIRED = Message(
        "cli.search_query_required",
        "Нужен запрос. Пример: rl search pizza",
        "Query required. Example: rl search pizza",
    )
    SEARCH_NEEDS_QUERY_OR_FILTERS = Message(
        "cli.search_needs_query_or_filters",
        "Нужен запрос или фильтр.",
        "Query or filter required.",
    )
    UPDATE_USE_PACKAGE_MANAGER = Message(
        "cli.update_use_package_manager",
        "roll не обновляет себя сам. Используйте пакетный менеджер, например `brew upgrade roll`, или переустановите пакет из исходников.",
        "roll does not self-update. Use your package manager, for example `brew upgrade roll`, or reinstall the package from source.",
    )
    TAGS_NORMALIZED = Message(
        "cli.tags_normalized", "Теги нормализованы.", "Tags normalized."
    )
    TAGS_ALREADY_NORMALIZED = Message(
        "cli.tags_already_normalized",
        "Теги уже нормализованы.",
        "Tags are already normalized.",
    )
    NORMALIZE_PHOTOS_CONFIRM_YEAR = Message(
        "cli.normalize_photos_confirm_year",
        "Год {year} верен",
        "Year {year} correct",
    )
    NORMALIZE_PHOTOS_YEAR = Message(
        "cli.normalize_photos_year", "Год для {folder}", "Year for {folder}"
    )
    NORMALIZE_PHOTOS_MONTH = Message(
        "cli.normalize_photos_month",
        "Месяц для {folder} [01-12]",
        "Month for {folder} [01-12]",
    )
    NORMALIZE_PHOTOS_MANUAL = Message(
        "cli.normalize_photos_manual", "Месяцы вручную?", "Manual months?"
    )
    NORMALIZE_PHOTOS_PREVIEW = Message(
        "cli.normalize_photos_preview", "План фото:", "Photo plan:"
    )
    NO_CHOICE = Message(
        "cli.no_choice", "Не удалось выбрать roll.", "Could not select a roll."
    )
    NO_CHOICES = Message(
        "cli.no_choices", "Нет доступных вариантов.", "No choices available."
    )
    STOCK_MISSING_DICT = Message(
        "cli.stock_missing_dict",
        "'{value}' отсутствует в словаре.\n\nДобавить? [Y/n] ",
        "'{value}' is missing from the dictionary.\n\nAdd it? [Y/n] ",
    )
    BATCH_WILL_PROCESS = Message(
        "cli.batch_will_process", "Будет обработано:", "Will process:"
    )
    BATCH_CONFIRM = Message(
        "cli.batch_confirm", "Пометить все как processed?", "Mark all as processed?"
    )
    BATCH_PROCESSED = Message("cli.batch_processed", "Обработано:", "Processed:")
    BATCH_NEEDS_FILTERS = Message(
        "cli.batch_needs_filters",
        "Нужен фильтр и изменение.",
        "Filter and change required.",
    )
    BATCH_FILTER_YEAR = Message("cli.batch_filter_year", "Год.", "Year.")
    BATCH_FILTER_FILM = Message(
        "cli.batch_filter_film",
        "Пленки через запятую.",
        "Films, comma-separated.",
    )
    BATCH_FILTER_CAMERA = Message(
        "cli.batch_filter_camera",
        "Камеры через запятую.",
        "Cameras, comma-separated.",
    )
    BATCH_FILTER_STATUS = Message(
        "cli.batch_filter_status",
        "Статусы через запятую.",
        "Statuses, comma-separated.",
    )
    BATCH_SET_STATUS = Message(
        "cli.batch_set_status", "Статус для выбранных роллов.", "Set status."
    )
    BATCH_SET_CAMERA = Message(
        "cli.batch_set_camera", "Камера для выбранных роллов.", "Set camera."
    )
    BATCH_ADD_FEATURE = Message(
        "cli.batch_add_feature",
        "Особенности через запятую.",
        "Features, comma-separated.",
    )
    BATCH_ADD_TAG = Message(
        "cli.batch_add_tag", "Теги через запятую.", "Tags, comma-separated."
    )
    BATCH_TITLE = Message("cli.batch_title", "Массовое редактирование", "Batch editing")
    STATS_YEAR = Message("cli.stats_year", "Год:", "Year:")
    STATS_ROLLS = Message("cli.stats_rolls", "Роллов:", "Rolls:")
    STATS_FILMS = Message("cli.stats_films", "Пленок:", "Films:")
    STATS_TAGS = Message("cli.stats_tags", "Тегов:", "Tags:")
    STATS_BY_STATUS = Message("cli.stats_by_status", "По статусам", "By status")
    STATS_BY_YEAR = Message("cli.stats_by_year", "По годам", "By year")
    STATS_BY_FILM = Message("cli.stats_by_film", "По пленкам", "By film")
    STATS_BY_TAG = Message("cli.stats_by_tag", "По тегам", "By tag")
    STATS_BY_CAMERA = Message("cli.stats_by_camera", "По камерам", "By camera")
    STATS_MORE = Message("cli.stats_more", "... и еще {count}", "... and {count} more")
    DOCTOR_CAN_FIX = Message("cli.doctor_can_fix", "Можно исправить:", "Can fix:")
    DOCTOR_CAN_ADD = Message(
        "cli.doctor_can_add", "Можно добавить в keywords:", "Can add to keywords:"
    )
    DOCTOR_FIXES_APPLIED = Message(
        "cli.doctor_fixes_applied", "Исправления применены.", "Fixes applied."
    )
    DOCTOR_KEYWORDS_APPLIED = Message(
        "cli.doctor_keywords_applied",
        "Исправления keywords применены.",
        "Keywords fixes applied.",
    )
    STOCK_READ_ERROR = Message(
        "cli.stock_read_error",
        "Не удалось прочитать запас пленки:",
        "Could not read film stock:",
    )
    STOCK_FORMAT_ERROR = Message(
        "cli.stock_format_error",
        "Неверный формат запаса пленки:",
        "Invalid film stock format:",
    )
    STOCK_NOT_POSITIVE = Message(
        "cli.stock_not_positive",
        "Количество должно быть положительным.",
        "Quantity must be positive.",
    )
    STOCK_INSUFFICIENT = Message(
        "cli.stock_insufficient",
        "В запасе недостаточно пленки.",
        "Not enough film in stock.",
    )
    STOCK_MISSING = Message(
        "cli.stock_missing", "Такой пленки нет в запасе.", "No such film in stock."
    )
    ROLL_READ_ERROR = Message(
        "cli.roll_read_error",
        "Не удалось прочитать roll.toml:",
        "Could not read roll.toml:",
    )
    ROLL_STATUS_INVALID = Message(
        "cli.roll_status_invalid",
        "Неверный status в roll.toml:",
        "Invalid status in roll.toml:",
    )
    ROLL_FORMAT_ERROR = Message(
        "cli.roll_format_error",
        "Неверный формат roll.toml:",
        "Invalid roll.toml format:",
    )
    LANGUAGE = Message("cli.language", "Язык:", "Language:")
    LANGUAGE_SET_TO = Message("cli.language_set_to", "Язык:", "Language:")
    ALLOWED_VALUES = Message(
        "cli.allowed_values", "Допустимые: EN, RU.", "Allowed: EN, RU."
    )

    RUN_TO_INITIALIZE = Message(
        "cli.run_to_initialize",
        "  rl init ~/your/archive/path",
        "  rl init ~/your/archive/path",
    )
    UNINITIALIZED_MESSAGE = Message(
        "cli.uninitialized_message",
        "Архив не инициализирован.\nЗапусти: rl init ~/your/archive/path",
        "Archive not initialized.\nRun: rl init ~/your/archive/path",
    )
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
        "\n".join(
            [
                str(CLI_UNINITIALIZED),
                "",
                "Run:",
                str(RUN_TO_INITIALIZE),
            ]
        ),
    )


RU = {
    value.key: value.ru
    for name, value in Msg.__dict__.items()
    if isinstance(value, Message)
}
EN = {
    value.key: value.en
    for name, value in Msg.__dict__.items()
    if isinstance(value, Message)
}
