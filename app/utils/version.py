# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Version sémantique — EPSP ES-SENIA"""
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_BUILD = 0  # Auto-incrémenté par GitHub Actions CI

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
VERSION_TAG = f"v{VERSION}"
APP_NAME = "EPSP CongeManager"


def get_version() -> str:
    return VERSION


def get_tag() -> str:
    return VERSION_TAG


def get_full_label() -> str:
    return f"{APP_NAME} v{VERSION}"
