# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Point d'entrée — EPSP ES-SENIA
Architecture thread-safe, zéro deadlock.
"""
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _init_db():
    """Initialisation DB — appelé AVANT tkinter."""
    from app.utils.database import initialize_database
    from app.utils.migration import migrer
    initialize_database()
    migrer()
    try:
        from app.utils.migration import migrer_services
        migrer_services()
    except Exception:
        pass


class AppRoot(ctk.CTk):
    """
    Fenêtre racine unique.
    Ne bloque JAMAIS le thread principal tkinter.
    """

    def __init__(self):
        super().__init__()

        from app.utils.theme import COULEURS, DIMENSIONS
        self._COULEURS   = COULEURS
        self._DIMENSIONS = DIMENSIONS

        w = DIMENSIONS["fenetre_w"]
        h = DIMENSIONS["fenetre_h"]
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(
            DIMENSIONS["fenetre_min_w"],
            DIMENSIONS["fenetre_min_h"])
        self.configure(fg_color=COULEURS["bg_principal"])
        self.title("EPSP ES-SENIA — Chargement…")
        self.protocol("WM_DELETE_WINDOW",
                      self._fermeture)

        # Masquer pendant splash
        self.withdraw()

        # Lancer splash IMMÉDIATEMENT
        # (aucun I/O dans __init__)
        self.after(50, self._afficher_splash)

    def _afficher_splash(self):
        from app.views.splash import SplashScreen
        SplashScreen(
            self,
            duree_ms=2400,
            callback=self._apres_splash)

    def _apres_splash(self):
        """Appelé depuis splash — thread principal."""
        self.deiconify()
        self.update_idletasks()
        self._demarrer()

    def _demarrer(self):
        from app.utils.database import get_config
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
            # Délai court — laisse tkinter respirer
            self.after(200, self._afficher_app)

        ecran = VueActivation(
            self,
            on_activation_complete=_apres)
        ecran.pack(fill="both", expand=True)
        self.update_idletasks()

    def _afficher_app(self):
        self._vider()
        from app.utils.database import get_config
        from app.utils.version import get_version
        poly = get_config("poly_nom") or "ES-SENIA"
        self.title(
            f"EPSP {poly} — "
            f"Gestionnaire Congés v{get_version()}")

        from app.views.app_principale import (
            AppPrincipale)
        app = AppPrincipale(self)
        app.pack(fill="both", expand=True)
        # Force le rendu immédiat
        self.update_idletasks()

    def _fermeture(self):
        try:
            from app.utils.database import faire_backup
            faire_backup("fermeture")
        except Exception:
            pass
        self.destroy()


def main():
    # DB init AVANT tkinter — pas de conflit
    _init_db()
    app = AppRoot()
    app.mainloop()


if __name__ == "__main__":
    main()
