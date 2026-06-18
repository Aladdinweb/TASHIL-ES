# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Point d'entrée — EPSP ES-SENIA"""
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from app.utils.database import (
    initialize_database, get_config)
from app.utils.migration import migrer
from app.utils.theme import COULEURS, DIMENSIONS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppRoot(ctk.CTk):
    """
    Fenêtre racine unique.
    Affiche soit l'écran d'activation,
    soit la vue principale — sans jamais détruire root.
    """

    def __init__(self):
        super().__init__()
        self.title(
            "EPSP ES-SENIA — Gestionnaire Congés")
        w = DIMENSIONS["fenetre_w"]
        h = DIMENSIONS["fenetre_h"]
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(
            DIMENSIONS["fenetre_min_w"],
            DIMENSIONS["fenetre_min_h"])
        self.configure(
            fg_color=COULEURS["bg_principal"])
        self.protocol(
            "WM_DELETE_WINDOW", self._fermeture)

        self._vue_courante = None
        self._demarrer()

    def _demarrer(self):
        if not get_config("activation_done"):
            self._afficher_activation()
        else:
            self._afficher_app_principale()

    def _vider(self):
        """Supprime tous les widgets enfants."""
        for widget in self.winfo_children():
            widget.destroy()
        self._vue_courante = None

    def _afficher_activation(self):
        self._vider()
        from app.views.vue_activation import (
            VueActivation)

        def _apres(code, nom):
            self.after(100,
                       self._afficher_app_principale)

        ecran = VueActivation(
            self,
            on_activation_complete=_apres)
        ecran.pack(fill="both", expand=True)
        self._vue_courante = ecran

    def _afficher_app_principale(self):
        self._vider()

        # Mettre à jour le titre avec poly_nom
        from app.utils.version import get_version
        poly = get_config("poly_nom") or "ES-SENIA"
        self.title(
            f"EPSP {poly} — "
            f"Gestionnaire Congés Annuels "
            f"v{get_version()}")

        # Charger la sidebar + vues dans self
        from app.views.app_principale import (
            AppPrincipale)
        app = AppPrincipale(self)
        app.pack(fill="both", expand=True)
        self._vue_courante = app

    def _fermeture(self):
        from app.utils.database import faire_backup
        try:
            faire_backup("fermeture")
        except Exception:
            pass
        self.destroy()


def main():
    initialize_database()
    migrer()
    app = AppRoot()
    app.mainloop()


if __name__ == "__main__":
    main()
