from __future__ import annotations

import os
from typing import ClassVar

from roll.app.workspace.config import load_lang


def detect_locale() -> str:
    config_lang = load_lang().upper()
    if config_lang in {"EN", "RU"}:
        return config_lang.lower()

    value = (
        os.environ.get("ROLL_LOCALE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
        or "ru"
    )
    value = value.split(".", 1)[0].split("_", 1)[0].lower()
    return "en" if value.startswith("en") else "ru"


class Message(str):
    locale: ClassVar[str] = detect_locale()

    def __new__(cls, key: str, ru: str, en: str | None = None):
        text = en if cls.locale == "en" and en is not None else ru
        obj = str.__new__(cls, text)
        obj.key = key
        obj.ru = ru
        obj.en = en or ru
        return obj


class Headers:
    CONFIG_HEADER = Message("cli.config_header", "Конфигурация:", "Configuration:")
    ARCHIVE_HEADER = Message("cli.archive_header", "Архив:", "Archive:")
    ARCHIVE_MISSING = Message("cli.archive_missing", "Архив не найден:", "Archive not found:")
    STATUS_HEADER = Message("cli.status_header", "Состояние индекса", "Index status")
    STATUS_ARCHIVE_FOLDERS = Message("cli.status_archive_folders", "Папок в архиве:", "Folders in archive:")
    STATUS_INDEXED = Message("cli.status_indexed", "Проиндексировано:", "Indexed:")
    STATUS_UNINDEXED = Message("cli.status_unindexed", "Не проиндексировано:", "Not indexed:")
    STATUS_UNINDEXED_FOLDERS = Message("cli.status_unindexed_folders", "Не проиндексированные папки:", "Unindexed folders:")
    STATUS_ROLLS = Message("cli.status_rolls", "Пленки по статусам:", "Films by status:")
    STATUS_NO_ROLL_TOML = Message("cli.status_no_roll_toml", "без roll.toml:", "without roll.toml:")
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
    CLI_UNINITIALIZED = Message("cli.uninitialized", "roll не инициализирован.", "roll is not initialized.")
    CLI_INITIALIZED = Message("cli.initialized", "roll инициализирован.", "roll initialized.")
    NO_RESULTS = Message("cli.no_results", "Ничего не найдено.", "Nothing found.")
    NO_STATS_DATA = Message("cli.no_stats_data", "Нет данных для статистики.", "No statistics data.")
    NO_ROLLS = Message("cli.no_rolls", "Нет роллов.", "No rolls.")
    NO_LOADED_ROLLS = Message("cli.no_loaded_rolls", "Нет загруженных пленок.", "No loaded films.")
    STOCK_EMPTY = Message("cli.stock_empty", "Запас пуст.", "Stock is empty.")
    STOCK_HEADER = Message("cli.stock_header", "Запас пленки", "Film stock")
    STOCK_EMPTY_MANUAL = Message(
        "cli.stock_empty_manual",
        "Запас пуст. Используй --manual для ручного ввода.",
        "Stock is empty. Use --manual for manual entry.",
    )
    INVALID_DATE = Message("cli.invalid_date", "Неверная дата.", "Invalid date.")
    INVALID_QUANTITY = Message("cli.invalid_quantity", "Количество должно быть положительным.", "Quantity must be positive.")
    ROLL_EXISTS = Message("cli.roll_exists", "Roll уже существует:", "Roll already exists:")
    CHOOSE_STOCK = Message("cli.choose_stock", "Выбери пленку из запаса.", "Choose a film from stock.")
    SEARCH_QUERY_REQUIRED = Message(
        "cli.search_query_required",
        "Нужно указать строку поиска. Пример: rl search pizza",
        "You need to provide a search query. Example: rl search pizza",
    )
    TAGS_NORMALIZED = Message("cli.tags_normalized", "Теги нормализованы.", "Tags normalized.")
    TAGS_ALREADY_NORMALIZED = Message("cli.tags_already_normalized", "Теги уже нормализованы.", "Tags are already normalized.")
    DOCTOR_FIX_HINT = Message("cli.doctor_fix_hint", "Запусти: rl doctor --fix", "Run: rl doctor --fix")
    NO_CHOICE = Message("cli.no_choice", "Не удалось выбрать roll.", "Could not select a roll.")

    RUN_TO_INITIALIZE = Message("cli.run_to_initialize", "  rl init ~/your/archive/path", "  rl init ~/your/archive/path")
    UNINITIALIZED_MESSAGE = Message(
        "cli.uninitialized_message",
        "roll не инициализирован.\nЗапусти: rl init ~/your/archive/path",
        "roll is not initialized.\nRun: rl init ~/your/archive/path",
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


RU = {value.key: value.ru for name, value in Msg.__dict__.items() if isinstance(value, Message)}
EN = {value.key: value.en for name, value in Msg.__dict__.items() if isinstance(value, Message)}
