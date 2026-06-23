# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Version sémantique — TASHIL"""
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_BUILD = 0  # Injecté par GitHub Actions

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
VERSION_TAG = f"v{VERSION}"

try:
    from app.config import APP_NAME, APP_TAGLINE
except Exception:
    APP_NAME    = "TASHIL"
    APP_TAGLINE = "Smart Health Management System"


def get_version() -> str:
    return VERSION


def get_tag() -> str:
    return VERSION_TAG


def get_full_label() -> str:
    return f"{APP_NAME} v{VERSION}"
