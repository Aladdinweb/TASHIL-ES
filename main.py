# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Point d'entrée — EPSP ES-SENIA"""
import sys, os
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
    def __init__(self):
        super().__init__()
        self.title("EPSP ES-SENIA")
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
        self.withdraw()
        self._afficher_splash()

    def _afficher_splash(self):
        from app.views.splash import SplashScreen
        SplashScreen(self, duree_ms=2500,
                     callback=self._apres_splash)

    def _apres_splash(self):
        self.deiconify()
        self._demarrer()

    def _demarrer(self):
        if not get_config("activation_done"):
            self._afficher_activation()
        else:
            self._afficher_app()

    def _vider(self):
        for w in self.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

    def _afficher_activation(self):
        self._vider()
        from app.views.vue_activation import (
            VueActivation)

        def _apres(code, nom):
            self.after(150, self._afficher_app)

        ecran = VueActivation(
            self, on_activation_complete=_apres)
        ecran.pack(fill="both", expand=True)

    def _afficher_app(self):
        self._vider()
        from app.utils.version import get_version
        poly = get_config("poly_nom") or "ES-SENIA"
        self.title(
            f"EPSP {poly} — "
            f"Gestionnaire Congés v{get_version()}")
        from app.views.app_principale import (
            AppPrincipale)
        app = AppPrincipale(self)
        app.pack(fill="both", expand=True)

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
    # Migrer colonne service
    try:
        from app.utils.migration import (
            migrer_services)
        migrer_services()
    except Exception:
        pass
    app = AppRoot()
    app.mainloop()


if __name__ == "__main__":
    main()
