# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Services et grades — source depuis config.py"""
from app.config import (
    SERVICES_CLINIQUES,
    HIERARCHIE_GRADES,
    POSTES_PAR_GRADE,
)

__all__ = [
    "SERVICES_CLINIQUES",
    "HIERARCHIE_GRADES",
    "POSTES_PAR_GRADE",
    "GRADES",
    "rang_grade",
]

# Alias pour compatibilité
GRADES = HIERARCHIE_GRADES


def rang_grade(grade: str) -> int:
    try:
        return HIERARCHIE_GRADES.index(grade)
    except ValueError:
        return len(HIERARCHIE_GRADES)
