class Msg:
    CLI_UNINITIALIZED = "roll is not initialized."
    CLI_INITIALIZED = "roll is initialized."
    CONFIG_HEADER = "Configuration"
    ARCHIVE_HEADER = "Archive:"
    ARCHIVE_MISSING = "Архив не найден:"
    SEARCH_NOT_IMPLEMENTED = "Search is not implemented yet:"
    INDEX_DONE = "Пленка проиндексирована."
    STATUS_HEADER = "Index status"
    STATUS_ARCHIVE_FOLDERS = "Archive folders:"
    STATUS_INDEXED = "Indexed:"
    STATUS_UNINDEXED = "Unindexed:"
    STATUS_UNINDEXED_FOLDERS = "Unindexed folders:"
    VOCAB_FILMS = "Films:"
    VOCAB_CAMERAS = "Cameras:"
    VOCAB_FEATURES = "Features:"
    VOCAB_KEYWORDS = "Keywords:"

    RUN_TO_INITIALIZE = "  rl init ~/your/archive/path"
    UNINITIALIZED_MESSAGE = "roll is not initialized.\nRun: rl init ~/your/archive/path"
    UNINITIALIZED_NOTICE = "\n".join(
        [
            CLI_UNINITIALIZED,
            "",
            "Запусти:",
            RUN_TO_INITIALIZE,
        ]
    )

    DOCTOR_OK = "OK"
    DOCTOR_ERROR_PREFIX = "ERROR:"
    DOCTOR_WARN_PREFIX = "WARN:"
    DOCTOR_NO_ARCHIVES = "Global config does not contain any archives."
    DOCTOR_ARCHIVE_MISSING = "Archive does not exist:"
    DOCTOR_WORKSPACE_MISSING = "Missing workspace directory:"
    DOCTOR_VOCAB_DIR_MISSING = "Missing vocabulary directory:"
    DOCTOR_VOCAB_FILE_MISSING = "Missing vocabulary file:"
    DOCTOR_ROLL_MISSING = "Missing roll.toml:"
    DOCTOR_ROLL_UNREADABLE = "Unreadable roll.toml:"
    DOCTOR_REQUIRED_FIELD_MISSING = "Missing required field"
    DOCTOR_FILM_NOT_IN_VOCAB = "Film is not in vocabulary:"
    DOCTOR_CAMERA_NOT_IN_VOCAB = "Camera is not in vocabulary:"
    DOCTOR_FEATURE_NOT_IN_VOCAB = "Feature is not in vocabulary:"
    DOCTOR_KEYWORD_NOT_IN_VOCAB = "Keyword is not in vocabulary:"
    DOCTOR_UNINDEXED_FOLDERS = "Unindexed folders:"
    DOCTOR_SUSPICIOUS_YEAR = "Suspicious year folder name:"
    DOCTOR_SUSPICIOUS_ROLL = "Suspicious roll folder name:"
