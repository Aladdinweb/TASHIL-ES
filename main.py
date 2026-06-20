# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Point d'entrée — EPSP ES-SENIA — Fix écran noir"""
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))


def _init_db():
    from app.utils.database import initialize_database
    from app.utils.migration import migrer
    initialize_database()
    migrer()
    try:
        from app.utils.migration import migrer_services
        migrer_services()
    except Exception:
        pass


def main():
    # 1. DB init AVANT tkinter
    _init_db()

    import customtkinter as ctk
    from app.utils.theme import COULEURS, DIMENSIONS
    from app.utils.database import get_config
    from app.utils.version import get_version

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()

    w = DIMENSIONS["fenetre_w"]
    h = DIMENSIONS["fenetre_h"]
    root.update_idletasks()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(
        DIMENSIONS["fenetre_min_w"],
        DIMENSIONS["fenetre_min_h"])
    root.configure(fg_color=COULEURS["bg_principal"])

    poly = get_config("poly_nom") or "ES-SENIA"
    root.title(
        f"EPSP {poly} — "
        f"Gestionnaire Congés v{get_version()}")

    def _fermeture():
        try:
            from app.utils.database import faire_backup
            faire_backup("fermeture")
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _fermeture)

    # 2. Décider quelle vue afficher
    activation_done = get_config("activation_done")

    def _lancer_app():
        """Vide root et charge AppPrincipale."""
        for w_child in root.winfo_children():
            try:
                w_child.destroy()
            except Exception:
                pass
        from app.views.app_principale import (
            AppPrincipale)
        frame = AppPrincipale(root)
        frame.pack(fill="both", expand=True)
        root.update_idletasks()

    def _lancer_activation():
        from app.views.vue_activation import (
            VueActivation)

        def _apres(code, nom):
            root.title(
                f"EPSP {nom} — "
                f"Gestionnaire Congés "
                f"v{get_version()}")
            root.after(100, _lancer_app)

        frame = VueActivation(
            root,
            on_activation_complete=_apres)
        frame.pack(fill="both", expand=True)
        root.update_idletasks()

    if not activation_done:
        root.after(100, _lancer_activation)
    else:
        root.after(100, _lancer_app)

    root.mainloop()


if __name__ == "__main__":
    main()
