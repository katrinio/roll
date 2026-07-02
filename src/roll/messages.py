CLI_UNINITIALIZED = "roll is not initialized."
CLI_INITIALIZED = "roll is initialized."
CONFIG_HEADER = "Configuration"
ARCHIVE_HEADER = "Archive:"
ARCHIVE_MISSING = "Архив не найден:"

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
