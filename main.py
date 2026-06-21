# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import initialize_database, get_config
from app.utils.migration import migrer

initialize_database()
migrer()

try:
    from app.utils.migration import migrer_services
    migrer_services()
except Exception:
    pass

import customtkinter as ctk
from app.utils.theme import COULEURS, DIMENSIONS
from app.utils.version import get_version

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
w, h = DIMENSIONS["fenetre_w"], DIMENSIONS["fenetre_h"]
root.update_idletasks()
x = (root.winfo_screenwidth()  - w) // 2
y = (root.winfo_screenheight() - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")
root.minsize(DIMENSIONS["fenetre_min_w"],
             DIMENSIONS["fenetre_min_h"])
root.configure(fg_color=COULEURS["bg_principal"])

poly = get_config("poly_nom") or "ES-SENIA"
root.title(f"EPSP {poly} — Gestionnaire Congés v{get_version()}")

def fermeture():
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", fermeture)


def lancer_app():
    from app.views.app_principale import AppPrincipale
    frame = AppPrincipale(root)
    frame.place(x=0, y=0, relwidth=1, relheight=1)
    root.update()


def lancer_activation():
    from app.views.vue_activation import VueActivation

    def apres(code, nom):
        for w in root.winfo_children():
            try: w.destroy()
            except: pass
        root.title(f"EPSP {nom} — "
                   f"Gestionnaire Congés v{get_version()}")
        root.after(50, lancer_app)

    frame = VueActivation(root,
                          on_activation_complete=apres)
    frame.place(x=0, y=0, relwidth=1, relheight=1)
    root.update()


if get_config("activation_done"):
    root.after(100, lancer_app)
else:
    root.after(100, lancer_activation)

root.mainloop()
