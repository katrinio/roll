from __future__ import annotations


class Doctor:
    # status
    OK = "OK"
    ERROR_PREFIX = "ERROR:"
    WARN_PREFIX = "WARN:"

    # global config
    NO_ARCHIVES = "No archives."
    GLOBAL_CONFIG_MISSING = "Missing global config:"
    GLOBAL_CONFIG_INVALID = "Invalid global config:"
    LANGUAGE_NOT_EXPLICIT = "Language not set explicitly; using EN."
    LANGUAGE_INVALID = "Invalid global config language:"
    GLOBAL_CONFIG_DUPLICATE_ARCHIVES = "Duplicate archives in global config:"
    ARCHIVE_NOT_DIRECTORY = "Archive is not a directory:"

    # archive and workspace
    ARCHIVE_MISSING = "Archive not found:"
    WORKSPACE_MISSING = "Missing .roll folder:"
    WORKSPACE_CONFIG_MISSING = "Missing workspace config:"
    WORKSPACE_CONFIG_INVALID = "Invalid workspace config:"
    WORKSPACE_CONFIG_MISMATCH = "Workspace config does not match archive:"
    WORKSPACE_CONFIG_ARCHIVE_MISSING = "Workspace config missing archive."
    WORKSPACE_STOCK_MISSING = "Missing stock.toml:"
    WORKSPACE_STOCK_INVALID = "Invalid stock.toml:"

    # vocabulary
    VOCAB_KEYWORDS_NOT_CANONICAL = "keywords.txt is not canonical:"
    VOCAB_DIR_MISSING = "Missing vocabulary folder:"
    VOCAB_FILE_MISSING = "Missing vocabulary file:"

    # roll metadata
    ROLL_MISSING = "Missing roll.toml:"
    ROLL_UNREADABLE = "Invalid roll.toml:"
    ROLL_LOADED_AT_MISMATCH = "loaded_at does not match folder name:"
    REQUIRED_FIELD_MISSING = "Missing required field:"

    # roll content
    FILM_NOT_IN_VOCAB = "Film not in vocabulary:"
    CAMERA_NOT_IN_VOCAB = "Camera not in vocabulary:"
    FEATURE_NOT_IN_VOCAB = "Feature not in vocabulary:"
    KEYWORD_NOT_IN_VOCAB = "Keyword not in vocabulary:"
    KEYWORD_NOT_NORMALIZED = "Keyword not uppercase:"

    # filesystem hygiene
    UNINDEXED_FOLDERS = "Unindexed folders:"
    SUSPICIOUS_YEAR = "Suspicious year name:"
    SUSPICIOUS_ROLL = "Suspicious folder name:"
