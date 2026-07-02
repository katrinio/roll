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
