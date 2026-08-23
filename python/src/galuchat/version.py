class Version:
    API = 2
    MODULE = "Galuchat"
    MAJOR = 0
    MINOR = 5
    # Backward-compatible alias for the historical misspelling.
    MINER = MINOR
    PATCH = 0
    STRING = f"{MODULE}/{MAJOR}.{MINOR}.{PATCH}"
