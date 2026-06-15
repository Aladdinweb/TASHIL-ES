# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Point d'entrée principal — EPSP ES-SENIA
Gestionnaire de Reliquats de Congé Annuel
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import initialize_database
from app.utils.migration import migrer
from app.views.fenetre_principale import FenetrePrincipale


def main():
    initialize_database()
    migrer()
    app = FenetrePrincipale()
    app.mainloop()


if __name__ == "__main__":
    main()
