# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys
import os

# ── Crash dump AVANT tout import ─────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_PATH  = os.path.join(_BASE_DIR, "tashil_boot_error.txt")

def _crash_dump(msg: str):
    try:
        with open(_LOG_PATH, "w",
                  encoding="utf-8") as f:
            f.write(msg)
    except Exception:
        pass

sys.path.insert(0, _BASE_DIR)

# ── Tous les imports dans try/except ─────────
try:
    import traceback
    import threading

    # DB
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

    # Config/version avec fallback
    try:
        from app.config import APP_FULL_NAME
    except Exception:
        APP_FULL_NAME = "TASHIL"
    try:
        from app.utils.version import (
            get_version, get_window_title,
            get_full_label)
    except Exception:
        def get_version():           return "1.1.0"
        def get_window_title(p=""): return f"TASHIL — {p}"
        def get_full_label():        return "TASHIL v1.1.0"

    # Tkinter
    import customtkinter as ctk
    from app.utils.theme import COULEURS, DIMENSIONS

except Exception as _boot_err:
    _crash_dump(
        f"BOOT ERROR\n\n"
        f"{traceback.format_exc() if 'traceback' in dir() else str(_boot_err)}")
    sys.exit(1)

# ── Fenêtre root ──────────────────────────────
try:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    W = DIMENSIONS["fenetre_w"]
    H = DIMENSIONS["fenetre_h"]
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(
        f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
    root.minsize(
        DIMENSIONS["fenetre_min_w"],
        DIMENSIONS["fenetre_min_h"])
    root.configure(
        fg_color=COULEURS["bg_principal"])
    poly = get_config("poly_nom") or "ES-SENIA"
    root.title(get_window_title(poly))
    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: (
            _backup_safe(),
            root.destroy()))

except Exception:
    _crash_dump(
        f"ROOT INIT ERROR\n\n"
        f"{traceback.format_exc()}")
    sys.exit(1)


def _backup_safe():
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass


# ── Erreur visible dans fenêtre ──────────────
def _afficher_erreur(msg: str):
    _crash_dump(f"RUNTIME ERROR\n\n{msg}")
    try:
        for w in root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        f = ctk.CTkFrame(
            root, fg_color="#0D0808",
            corner_radius=0)
        f.place(x=0, y=0,
                relwidth=1, relheight=1)
        ctk.CTkLabel(
            f, text="⚠  Erreur TASHIL",
            font=("Segoe UI", 18, "bold"),
            text_color="#EF4444"
        ).place(relx=0.5, rely=0.15,
                anchor="center")
        ctk.CTkLabel(
            f, text=str(msg)[:700],
            font=("Courier", 9),
            text_color="#FCA5A5",
            wraplength=680, justify="left"
        ).place(relx=0.5, rely=0.52,
                anchor="center")
        ctk.CTkLabel(
            f,
            text=f"Détails : {_LOG_PATH}",
            font=("Segoe UI", 8),
            text_color="#64748B"
        ).place(relx=0.5, rely=0.75,
                anchor="center")
        ctk.CTkButton(
            f, text="Quitter",
            fg_color="#DC2626",
            hover_color="#991B1B",
            command=root.destroy,
            width=130, height=38,
            corner_radius=6
        ).place(relx=0.5, rely=0.86,
                anchor="center")
    except Exception:
        pass


# ── Splash ────────────────────────────────────
def _build_splash():
    try:
        sp = ctk.CTkToplevel(root)
        sp.overrideredirect(True)
        sp.attributes("-topmost", True)
        sp.attributes("-alpha", 0.0)
        sp.configure(fg_color="#060D1A")
        sp.resizable(False, False)
        sw2 = root.winfo_screenwidth()
        sh2 = root.winfo_screenheight()
        w, h = 460, 280
        sp.geometry(
            f"{w}x{h}+{(sw2-w)//2}"
            f"+{(sh2-h)//2}")

        fond = ctk.CTkFrame(
            sp, fg_color="#060D1A",
            corner_radius=0)
        fond.place(x=0, y=0,
                   relwidth=1, relheight=1)

        ctk.CTkLabel(
            fond, text="⚕  TASHIL",
            font=("Segoe UI", 30, "bold"),
            text_color="#3B82F6"
        ).place(relx=0.5, y=40, anchor="n")

        ctk.CTkLabel(
            fond,
            text="Smart Health Management System",
            font=("Segoe UI", 10),
            text_color="#64748B"
        ).place(relx=0.5, y=84, anchor="n")

        ctk.CTkLabel(
            fond, text="🇩🇿",
            font=("Segoe UI", 36)
        ).place(relx=0.5, y=110, anchor="n")

        ctk.CTkLabel(
            fond,
            text="وزارة الصحة  —  "
                 "الجمهورية الجزائرية",
            font=("Segoe UI", 10),
            text_color="#94A3B8"
        ).place(relx=0.5, y=158, anchor="n")

        barre = ctk.CTkProgressBar(
            fond, mode="determinate",
            fg_color="#0F1E35",
            progress_color="#2563EB",
            height=4, corner_radius=2)
        barre.place(x=50, y=196,
                    relwidth=1, width=-100)
        barre.set(0)

        lbl = ctk.CTkLabel(
            fond, text=get_full_label(),
            font=("Segoe UI", 9),
            text_color="#334155")
        lbl.place(relx=0.5, y=210, anchor="n")

        ctk.CTkLabel(
            fond,
            text="ILINE TECH 2026 — "
                 "FERAK ALADDIN",
            font=("Segoe UI", 7),
            text_color="#1E293B"
        ).place(relx=0.5, y=256, anchor="n")

        def fade_in(a=0.0):
            a = min(1.0, a + 0.07)
            sp.attributes("-alpha", a)
            if a < 1.0:
                sp.after(15,
                         lambda: fade_in(a))
            else:
                sp.after(10,
                         lambda: progress(0.0))

        def progress(v=0.0):
            if v <= 1.0:
                barre.set(v)
                lbl.configure(
                    text=f"Chargement…  "
                         f"{get_full_label()}")
                sp.after(
                    16,
                    lambda: progress(
                        round(v + 0.014, 3)))
            else:
                sp.after(200,
                         lambda: fade_out(1.0))

        def fade_out(a=1.0):
            a = max(0.0, a - 0.07)
            sp.attributes("-alpha", a)
            if a > 0.0:
                sp.after(15,
                         lambda: fade_out(a))
            else:
                try:
                    sp.destroy()
                except Exception:
                    pass
                root.after(30, _apres_splash)

        sp.after(10, lambda: fade_in(0.0))

    except Exception:
        # Splash raté → lancer app quand même
        root.after(100, _apres_splash)


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
        _afficher_erreur(traceback.format_exc())


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
        _afficher_erreur(traceback.format_exc())


def _apres_splash():
    try:
        root.deiconify()
        root.update_idletasks()
        if get_config("activation_done"):
            _lancer_app()
        else:
            _lancer_activation()
    except Exception:
        _afficher_erreur(traceback.format_exc())


# ── Smart Hub daemon (optionnel) ──────────────
def _hub():
    try:
        import socket
        s = socket.socket()
        s.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, 1)
        s.settimeout(1.0)
        s.bind(("0.0.0.0", 7890))
        s.listen(3)
        while True:
            try:
                c, _ = s.accept()
                c.close()
            except socket.timeout:
                continue
            except Exception:
                break
        s.close()
    except Exception:
        pass  # Non bloquant


threading.Thread(
    target=_hub, daemon=True,
    name="SmartHub").start()

# ── Démarrage ─────────────────────────────────
root.withdraw()
root.after(50, _build_splash)
root.mainloop()
