# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os, traceback
sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

# ── DB init avant tkinter ─────────────────────
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
    sys.exit(1)

# ── Config & version ──────────────────────────
try:
    from app.config import APP_FULL_NAME
    from app.utils.version import (
        get_version, get_window_title,
        get_full_label)
except Exception:
    APP_FULL_NAME = "TASHIL"
    def get_version():          return "1.1.0"
    def get_window_title(p=""): return f"TASHIL — {p}"
    def get_full_label():       return "TASHIL v1.1.0"

# ── Tkinter ───────────────────────────────────
try:
    import customtkinter as ctk
    from app.utils.theme import COULEURS, DIMENSIONS
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
root.minsize(DIMENSIONS["fenetre_min_w"],
             DIMENSIONS["fenetre_min_h"])
root.configure(fg_color=COULEURS["bg_principal"])

poly = get_config("poly_nom") or "ES-SENIA"
root.title(get_window_title(poly))


def _fermeture():
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass
    root.destroy()


root.protocol("WM_DELETE_WINDOW", _fermeture)


# ── Splash minimal ────────────────────────────
class SplashTASHIL(ctk.CTkToplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self._cb     = callback
        self._parent = parent
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#060D1A")
        self.resizable(False, False)
        w, h = 480, 300
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        self.geometry(
            f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()
        self.after(20, self._fade_in)

    def _build(self):
        fond = ctk.CTkFrame(
            self, fg_color="#060D1A",
            corner_radius=0)
        fond.place(x=0, y=0,
                   relwidth=1, relheight=1)

        ctk.CTkLabel(
            fond, text="⚕  TASHIL",
            font=("Segoe UI", 32, "bold"),
            text_color="#3B82F6"
        ).place(relx=0.5, y=60, anchor="n")

        ctk.CTkLabel(
            fond,
            text="Smart Health Management System",
            font=("Segoe UI", 11),
            text_color="#64748B"
        ).place(relx=0.5, y=106, anchor="n")

        ctk.CTkLabel(
            fond, text="🇩🇿",
            font=("Segoe UI", 40)
        ).place(relx=0.5, y=140, anchor="n")

        ctk.CTkLabel(
            fond,
            text="الجمهورية الجزائرية الديمقراطية الشعبية",
            font=("Segoe UI", 10),
            text_color="#94A3B8"
        ).place(relx=0.5, y=192, anchor="n")

        self.barre = ctk.CTkProgressBar(
            fond, mode="determinate",
            fg_color="#0F1E35",
            progress_color="#2563EB",
            height=4, corner_radius=2)
        self.barre.place(x=50, y=232,
                         relwidth=1, width=-100)
        self.barre.set(0)

        self.lbl = ctk.CTkLabel(
            fond, text=get_full_label(),
            font=("Segoe UI", 9),
            text_color="#334155")
        self.lbl.place(relx=0.5, y=246,
                       anchor="n")

    def _fade_in(self, a=0.0):
        a = min(1.0, a + 0.08)
        self.attributes("-alpha", a)
        if a < 1.0:
            self.after(14,
                       lambda: self._fade_in(a))
        else:
            self.after(10, self._progress)

    def _progress(self, v=0.0):
        if v <= 1.0:
            self.barre.set(v)
            self.after(
                16,
                lambda: self._progress(
                    round(v + 0.015, 3)))
        else:
            self.after(200, self._fade_out)

    def _fade_out(self, a=1.0):
        a = max(0.0, a - 0.08)
        self.attributes("-alpha", a)
        if a > 0.0:
            self.after(14,
                       lambda: self._fade_out(a))
        else:
            try:
                self.destroy()
            except Exception:
                pass
            if self._cb:
                try:
                    self._parent.after(
                        30, self._cb)
                except Exception:
                    pass


# ── Erreur visible ────────────────────────────
def _afficher_erreur(msg: str):
    for w in root.winfo_children():
        try:
            w.destroy()
        except Exception:
            pass
    f = ctk.CTkFrame(
        root, fg_color="#0D0808",
        corner_radius=0)
    f.place(x=0, y=0, relwidth=1, relheight=1)

    ctk.CTkLabel(
        f, text="⚠  Erreur TASHIL",
        font=("Segoe UI", 18, "bold"),
        text_color="#EF4444"
    ).place(relx=0.5, rely=0.18,
            anchor="center")

    ctk.CTkLabel(
        f, text=str(msg)[:800],
        font=("Courier", 9),
        text_color="#FCA5A5",
        wraplength=680, justify="left"
    ).place(relx=0.5, rely=0.52,
            anchor="center")

    ctk.CTkButton(
        f, text="Quitter",
        fg_color="#DC2626",
        hover_color="#991B1B",
        command=root.destroy,
        width=130, height=38,
        corner_radius=6
    ).place(relx=0.5, rely=0.84,
            anchor="center")


# ── Lancement app ─────────────────────────────
def _lancer_app():
    try:
        for w in root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
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
            try:
                w.destroy()
            except Exception:
                pass
        from app.views.vue_activation import (
            VueActivation)

        def _apres(code, nom):
            root.title(get_window_title(nom))
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


def _apres_splash():
    root.deiconify()
    root.update_idletasks()
    if get_config("activation_done"):
        _lancer_app()
    else:
        _lancer_activation()


# ── Smart Hub — daemon non bloquant ──────────
def _demarrer_smart_hub():
    """Socket serveur optionnel — jamais bloquant."""
    try:
        import socket
        import json
        import base64
        import datetime

        srv = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)
        srv.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, 1)
        srv.settimeout(1.0)
        srv.bind(("0.0.0.0", 7890))
        srv.listen(3)
        print("[SmartHub] Actif sur port 7890")

        while True:
            try:
                conn, addr = srv.accept()
                conn.close()
            except socket.timeout:
                continue
            except Exception:
                break
        srv.close()
    except Exception as ex:
        # Non bloquant — l'app démarre quand même
        print(f"[SmartHub] Non disponible: {ex}")


import threading
threading.Thread(
    target=_demarrer_smart_hub,
    daemon=True,
    name="SmartHub"
).start()

# ── Démarrage ─────────────────────────────────
root.withdraw()
root.after(
    50,
    lambda: SplashTASHIL(
        root, callback=_apres_splash))

root.mainloop()
