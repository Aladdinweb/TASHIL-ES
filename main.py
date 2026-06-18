# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Point d'entrée — EPSP ES-SENIA"""
import sys
import os
import customtkinter as ctk

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import (
    initialize_database, get_config)
from app.utils.migration import migrer
from app.utils.theme import COULEURS, DIMENSIONS


def main():
    initialize_database()
    migrer()

    # Fenêtre racine
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("EPSP ES-SENIA — Gestionnaire Congés")

    w = DIMENSIONS["fenetre_w"]
    h = DIMENSIONS["fenetre_h"]
    root.update_idletasks()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(DIMENSIONS["fenetre_min_w"],
                 DIMENSIONS["fenetre_min_h"])
    root.configure(fg_color=COULEURS["bg_principal"])

    activation_done = get_config("activation_done")

    if not activation_done:
        # ── Écran d'activation ────────────────────────────
        from app.views.vue_activation import VueActivation

        def _apres_activation(code, nom):
            for w_child in root.winfo_children():
                w_child.destroy()
            _lancer_app(root)

        ecran = VueActivation(
            root,
            on_activation_complete=_apres_activation)
        ecran.pack(fill="both", expand=True)

    else:
        _lancer_app(root)

    root.mainloop()


def _lancer_app(root: ctk.CTk):
    """Lance la fenêtre principale dans root."""
    from app.views.fenetre_principale import (
        FenetrePrincipale)
    # Détruire root et créer FenetrePrincipale
    root.destroy()
    app = FenetrePrincipale()
    app.mainloop()


if __name__ == "__main__":
    main()
