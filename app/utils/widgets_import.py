# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Réexportation centralisée des widgets pour éviter les imports circulaires.
"""
from app.views.widgets import (
    CarteStatistique,
    BoutonAction,
    SeparateurH,
    TitreSection,
    ChampSaisie,
    MenuDeroulant,
    TableauListe,
)

__all__ = [
    "CarteStatistique", "BoutonAction", "SeparateurH",
    "TitreSection", "ChampSaisie", "MenuDeroulant", "TableauListe",
]
