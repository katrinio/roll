from roll.messages.cli import Message


class Doctor:
    OK = Message("doctor.ok", "OK", "OK")
    ERROR_PREFIX = Message("doctor.error_prefix", "ERROR:", "ERROR:")
    WARN_PREFIX = Message("doctor.warn_prefix", "WARN:", "WARN:")
    NO_ARCHIVES = Message(
        "doctor.no_archives",
        "В глобальной конфигурации нет архивов.",
        "There are no archives in the global config.",
    )
    ARCHIVE_MISSING = Message(
        "doctor.archive_missing", "Архив не найден:", "Archive not found:"
    )
    WORKSPACE_MISSING = Message(
        "doctor.workspace_missing", "Нет папки .roll:", "Missing .roll folder:"
    )
    WORKSPACE_CONFIG_MISSING = Message(
        "doctor.workspace_config_missing",
        "Нет файла workspace config:",
        "Missing workspace config file:",
    )
    WORKSPACE_CONFIG_MISMATCH = Message(
        "doctor.workspace_config_mismatch",
        "Workspace config не совпадает с архивом:",
        "Workspace config does not match archive:",
    )
    VOCAB_DIR_MISSING = Message(
        "doctor.vocab_dir_missing", "Нет папки словарей:", "Missing vocabulary folder:"
    )
    VOCAB_FILE_MISSING = Message(
        "doctor.vocab_file_missing", "Нет файла словаря:", "Missing vocabulary file:"
    )
    ROLL_MISSING = Message(
        "doctor.roll_missing", "Нет файла roll.toml:", "Missing roll.toml file:"
    )
    ROLL_UNREADABLE = Message(
        "doctor.roll_unreadable",
        "Не удалось прочитать roll.toml:",
        "Could not read roll.toml:",
    )
    REQUIRED_FIELD_MISSING = Message(
        "doctor.required_field_missing",
        "Нет обязательного поля",
        "Required field missing",
    )
    FILM_NOT_IN_VOCAB = Message(
        "doctor.film_not_in_vocab", "Пленка не в словаре:", "Film is not in vocabulary:"
    )
    CAMERA_NOT_IN_VOCAB = Message(
        "doctor.camera_not_in_vocab",
        "Камера не в словаре:",
        "Camera is not in vocabulary:",
    )
    FEATURE_NOT_IN_VOCAB = Message(
        "doctor.feature_not_in_vocab",
        "Особенность не в словаре:",
        "Feature is not in vocabulary:",
    )
    KEYWORD_NOT_IN_VOCAB = Message(
        "doctor.keyword_not_in_vocab",
        "Ключевое слово не в словаре:",
        "Keyword is not in vocabulary:",
    )
    KEYWORD_NOT_NORMALIZED = Message(
        "doctor.keyword_not_normalized",
        "Ключевое слово не в uppercase:",
        "Keyword is not uppercase:",
    )
    UNINDEXED_FOLDERS = Message(
        "doctor.unindexed_folders", "Не проиндексировано папок:", "Unindexed folders:"
    )
    SUSPICIOUS_YEAR = Message(
        "doctor.suspicious_year", "Подозрительное имя года:", "Suspicious year name:"
    )
    SUSPICIOUS_ROLL = Message(
        "doctor.suspicious_roll", "Подозрительное имя папки:", "Suspicious folder name:"
    )


RU = {
    value.key: str(value)
    for name, value in Doctor.__dict__.items()
    if isinstance(value, Message)
}
