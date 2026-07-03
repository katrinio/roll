from roll.messages.cli import Message


class Doctor:
    OK = Message("doctor.ok", "OK")
    ERROR_PREFIX = Message("doctor.error_prefix", "ERROR:")
    WARN_PREFIX = Message("doctor.warn_prefix", "WARN:")
    NO_ARCHIVES = Message("doctor.no_archives", "В глобальной конфигурации нет архивов.")
    ARCHIVE_MISSING = Message("doctor.archive_missing", "Архив не найден:")
    WORKSPACE_MISSING = Message("doctor.workspace_missing", "Нет папки .roll:")
    WORKSPACE_CONFIG_MISSING = Message("doctor.workspace_config_missing", "Нет файла workspace config:")
    WORKSPACE_CONFIG_MISMATCH = Message("doctor.workspace_config_mismatch", "Workspace config не совпадает с архивом:")
    VOCAB_DIR_MISSING = Message("doctor.vocab_dir_missing", "Нет папки словарей:")
    VOCAB_FILE_MISSING = Message("doctor.vocab_file_missing", "Нет файла словаря:")
    ROLL_MISSING = Message("doctor.roll_missing", "Нет файла roll.toml:")
    ROLL_UNREADABLE = Message("doctor.roll_unreadable", "Не удалось прочитать roll.toml:")
    REQUIRED_FIELD_MISSING = Message("doctor.required_field_missing", "Нет обязательного поля")
    FILM_NOT_IN_VOCAB = Message("doctor.film_not_in_vocab", "Пленка не в словаре:")
    CAMERA_NOT_IN_VOCAB = Message("doctor.camera_not_in_vocab", "Камера не в словаре:")
    FEATURE_NOT_IN_VOCAB = Message("doctor.feature_not_in_vocab", "Особенность не в словаре:")
    KEYWORD_NOT_IN_VOCAB = Message("doctor.keyword_not_in_vocab", "Ключевое слово не в словаре:")
    KEYWORD_NOT_NORMALIZED = Message("doctor.keyword_not_normalized", "Ключевое слово не в uppercase:")
    UNINDEXED_FOLDERS = Message("doctor.unindexed_folders", "Не проиндексировано папок:")
    SUSPICIOUS_YEAR = Message("doctor.suspicious_year", "Подозрительное имя года:")
    SUSPICIOUS_ROLL = Message("doctor.suspicious_roll", "Подозрительное имя папки:")


RU = {value.key: str(value) for name, value in Doctor.__dict__.items() if isinstance(value, Message)}
