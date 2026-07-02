class Headers:
    CONFIG_HEADER = "Configuration:"
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

class Msg(Headers):
    CLI_UNINITIALIZED = "roll is not initialized."
    CLI_INITIALIZED = "roll is initialized."

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

class Doctor:
    OK = "OK"
    ERROR_PREFIX = "ERROR:"
    WARN_PREFIX = "WARN:"
    NO_ARCHIVES = "Global config does not contain any archives."
    ARCHIVE_MISSING = "Archive does not exist:"
    WORKSPACE_MISSING = "Missing workspace directory:"
    VOCAB_DIR_MISSING = "Missing vocabulary directory:"
    VOCAB_FILE_MISSING = "Missing vocabulary file:"
    ROLL_MISSING = "Missing roll.toml:"
    ROLL_UNREADABLE = "Unreadable roll.toml:"
    REQUIRED_FIELD_MISSING = "Missing required field"
    FILM_NOT_IN_VOCAB = "Film is not in vocabulary:"
    CAMERA_NOT_IN_VOCAB = "Camera is not in vocabulary:"
    FEATURE_NOT_IN_VOCAB = "Feature is not in vocabulary:"
    KEYWORD_NOT_IN_VOCAB = "Keyword is not in vocabulary:"
    UNINDEXED_FOLDERS = "Unindexed folders:"
    SUSPICIOUS_YEAR = "Suspicious year folder name:"
    SUSPICIOUS_ROLL = "Suspicious roll folder name:"
