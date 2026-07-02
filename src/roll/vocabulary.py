from roll.dictionaries import Dictionary, DICTIONARIES_DIR

FILMS = Dictionary("films", DICTIONARIES_DIR / "films.txt")
CAMERAS = Dictionary("cameras", DICTIONARIES_DIR / "cameras.txt")
FEATURES = Dictionary("features", DICTIONARIES_DIR / "features.txt")
KEYWORDS = Dictionary("keywords", DICTIONARIES_DIR / "keywords.txt")
