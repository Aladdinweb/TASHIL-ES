# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Point d'entrée — EPSP ES-SENIA
Gestionnaire de Reliquats de Congé Annuel
"""
import sys
import os

# Chemins compatibles PyInstaller
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import initialize_database
from app.views.fenetre_principale import FenetrePrincipale


def main():
    # Initialiser la base de données au démarrage
    initialize_database()

    # Lancer l'interface graphique
    app = FenetrePrincipale()
    app.mainloop()


if __name__ == "__main__":
    main()
