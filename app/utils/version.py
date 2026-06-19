# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Version sémantique — injectée par GitHub Actions CI/CD"""
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_BUILD = 9  # Auto-incrémenté par CI

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
VERSION_TAG = f"v{VERSION}"
APP_NAME = "EPSP CongeManager"
BUILD_DATE = "2026"


def get_version() -> str:
    return VERSION


def get_tag() -> str:
    return VERSION_TAG


def get_full_label() -> str:
    return f"{APP_NAME} {VERSION_TAG}"
