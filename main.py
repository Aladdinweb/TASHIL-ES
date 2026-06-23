# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Point d'entrée TASHIL — place() partout"""
import sys, os, traceback
sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

# ── Config & version ──────────────────────────
try:
    from app.config import APP_FULL_NAME
    from app.utils.version import get_version
except Exception:
    APP_FULL_NAME = "TASHIL"
    def get_version(): return "1.1.0"

# ── Init DB avant tkinter ─────────────────────
try:
    from app.utils.database import (
        initialize_database, get_config)
    from app.utils.migration import migrer
    initialize_database()
    migrer()
    try:
        from app.utils.migration import (
            migrer_services)
        migrer_services()
    except Exception:
        pass
except Exception as e:
    print(f"[FATAL DB] {e}")
    traceback.print_exc()
    sys.exit(1)

# ── Tkinter ───────────────────────────────────
try:
    import customtkinter as ctk
    from app.utils.theme import (
        COULEURS, DIMENSIONS)
except Exception as e:
    print(f"[FATAL IMPORT] {e}")
    sys.exit(1)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
W = DIMENSIONS["fenetre_w"]
H = DIMENSIONS["fenetre_h"]
root.update_idletasks()
x = (root.winfo_screenwidth()  - W) // 2
y = (root.winfo_screenheight() - H) // 2
root.geometry(f"{W}x{H}+{x}+{y}")
root.minsize(
    DIMENSIONS["fenetre_min_w"],
    DIMENSIONS["fenetre_min_h"])
root.configure(fg_color=COULEURS["bg_principal"])

poly = get_config("poly_nom") or "ES-SENIA"
root.title(
    f"{APP_FULL_NAME} — {poly} "
    f"v{get_version()}")


def _fermeture():
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass
    root.destroy()


root.protocol("WM_DELETE_WINDOW", _fermeture)


# ── Affichage erreur dans fenêtre ────────────
def _afficher_erreur(msg: str):
    for w in root.winfo_children():
        try: w.destroy()
        except: pass
    f = ctk.CTkFrame(
        root, fg_color="#0D0808",
        corner_radius=0)
    f.place(x=0, y=0,
            relwidth=1, relheight=1)
    ctk.CTkLabel(
        f,
        text="⚠  Erreur de démarrage",
        font=("Segoe UI", 18, "bold"),
        text_color="#EF4444"
    ).place(relx=0.5, rely=0.25,
            anchor="center")
    ctk.CTkLabel(
        f, text=msg[:900],
        font=("Courier", 9),
        text_color="#FCA5A5",
        wraplength=680,
        justify="left"
    ).place(relx=0.5, rely=0.52,
            anchor="center")
    ctk.CTkButton(
        f, text="Quitter",
        fg_color="#DC2626",
        hover_color="#991B1B",
        command=root.destroy,
        width=130, height=38
    ).place(relx=0.5, rely=0.82,
            anchor="center")


# ── Lancement principal ───────────────────────
def _lancer_app():
    try:
        for w in root.winfo_children():
            try: w.destroy()
            except: pass
        from app.views.app_principale import (
            AppPrincipale)
        frame = AppPrincipale(root)
        frame.place(x=0, y=0,
                    relwidth=1, relheight=1)
        root.update_idletasks()
    except Exception:
        err = traceback.format_exc()
        print(f"[FATAL APP]\n{err}")
        _afficher_erreur(err)


def _lancer_activation():
    try:
        for w in root.winfo_children():
            try: w.destroy()
            except: pass
        from app.views.vue_activation import (
            VueActivation)

        def _apres(code, nom):
            root.title(
                f"{APP_FULL_NAME} — {nom} "
                f"v{get_version()}")
            root.after(80, _lancer_app)

        frame = VueActivation(
            root,
            on_activation_complete=_apres)
        frame.place(x=0, y=0,
                    relwidth=1, relheight=1)
        root.update_idletasks()
    except Exception:
        err = traceback.format_exc()
        print(f"[FATAL ACTIVATION]\n{err}")
        _afficher_erreur(err)


# Démarrage
if get_config("activation_done"):
    root.after(80, _lancer_app)
else:
    root.after(80, _lancer_activation)

root.mainloop()
