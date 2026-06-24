# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Version sémantique — TASHIL
Ancre production : v1.1.0
Patch injecté automatiquement par GitHub Actions CI.
"""

VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_BUILD = 0  # Remplacé par CI : git rev-list --count HEAD

VERSION     = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
VERSION_TAG = f"v{VERSION}"

# Import config avec fallback sécurisé
try:
    from app.config import APP_NAME, APP_TAGLINE
except Exception:
    APP_NAME    = "TASHIL"
    APP_TAGLINE = "Smart Health Management System"


def get_version() -> str:
    """Retourne la version courante ex: 1.1.0"""
    return VERSION


def get_tag() -> str:
    """Retourne le tag ex: v1.1.0"""
    return VERSION_TAG


def get_full_label() -> str:
    """Retourne: TASHIL v1.1.0"""
    return f"{APP_NAME} v{VERSION}"


def get_window_title(poly: str = "") -> str:
    """Retourne le titre complet de la fenêtre."""
    try:
        from app.config import APP_FULL_NAME
        base = APP_FULL_NAME
    except Exception:
        base = f"{APP_NAME}: {APP_TAGLINE}"
    if poly:
        return f"{base} — {poly} — v{VERSION}"
    return f"{base} — v{VERSION}"
