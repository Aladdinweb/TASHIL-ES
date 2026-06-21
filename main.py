# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Init DB (avant tkinter) ───────────────────
try:
    from app.utils.database import (
        initialize_database, get_config)
    from app.utils.migration import migrer
    initialize_database()
    migrer()
    try:
        from app.utils.migration import migrer_services
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
    from app.utils.theme import COULEURS, DIMENSIONS
    from app.utils.version import get_version
except Exception as e:
    print(f"[FATAL IMPORT] {e}")
    traceback.print_exc()
    sys.exit(1)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
w = DIMENSIONS["fenetre_w"]
h = DIMENSIONS["fenetre_h"]
root.update_idletasks()
x = (root.winfo_screenwidth()  - w) // 2
y = (root.winfo_screenheight() - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")
root.minsize(DIMENSIONS["fenetre_min_w"],
             DIMENSIONS["fenetre_min_h"])
root.configure(fg_color=COULEURS["bg_principal"])

poly = get_config("poly_nom") or "ES-SENIA"
root.title(
    f"EPSP {poly} — "
    f"Gestionnaire Congés v{get_version()}")

def fermeture():
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fermeture)

# ── Frame d'erreur si crash ───────────────────
def afficher_erreur(msg: str):
    """Affiche l'erreur dans la fenêtre."""
    import customtkinter as ctk
    f = ctk.CTkFrame(root,
                     fg_color="#1A0A0A",
                     corner_radius=0)
    f.place(x=0, y=0, relwidth=1, relheight=1)
    ctk.CTkLabel(
        f, text="⚠  Erreur de démarrage",
        font=("Segoe UI", 18, "bold"),
        text_color="#EF4444"
    ).place(relx=0.5, rely=0.3, anchor="center")
    ctk.CTkLabel(
        f, text=msg,
        font=("Courier", 10),
        text_color="#FCA5A5",
        wraplength=700,
        justify="left"
    ).place(relx=0.5, rely=0.55, anchor="center")
    ctk.CTkButton(
        f, text="Quitter",
        fg_color="#DC2626",
        command=root.destroy,
        width=120, height=36
    ).place(relx=0.5, rely=0.8, anchor="center")

# ── Lancement ─────────────────────────────────
def lancer_app():
    try:
        from app.views.app_principale import (
            AppPrincipale)
        frame = AppPrincipale(root)
        frame.place(x=0, y=0,
                    relwidth=1, relheight=1)
        root.update_idletasks()
    except Exception as e:
        err = traceback.format_exc()
        print(f"[FATAL APP] {err}")
        afficher_erreur(str(err)[:800])


def lancer_activation():
    try:
        from app.views.vue_activation import (
            VueActivation)

        def apres(code, nom):
            for child in root.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            root.title(
                f"EPSP {nom} — "
                f"Gestionnaire Congés "
                f"v{get_version()}")
            root.after(50, lancer_app)

        frame = VueActivation(
            root,
            on_activation_complete=apres)
        frame.place(x=0, y=0,
                    relwidth=1, relheight=1)
        root.update_idletasks()
    except Exception as e:
        err = traceback.format_exc()
        print(f"[FATAL ACTIVATION] {err}")
        afficher_erreur(str(err)[:800])


if get_config("activation_done"):
    root.after(100, lancer_app)
else:
    root.after(100, lancer_activation)

root.mainloop()
