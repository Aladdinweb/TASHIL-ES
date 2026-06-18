# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Version de l'application"""
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_BUILD = 0

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"

def get_version() -> str:
    return VERSION

def get_tag() -> str:
    return f"v{VERSION}"
