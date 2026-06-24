# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
TASHIL: Smart Health Management System
Point d'entrée principal — place() partout.
Splash animé + Smart Hub daemon en arrière-plan.
"""
import sys
import os
import threading
import traceback

sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)))

# ════════════════════════════════════════════════
# 1. INITIALISATION DB — AVANT TKINTER
# ════════════════════════════════════════════════
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

# ════════════════════════════════════════════════
# 2. CONFIG & VERSION — AVEC FALLBACK
# ════════════════════════════════════════════════
try:
    from app.config import (
        APP_FULL_NAME,
        SMART_HUB_HOST,
        SMART_HUB_PORT,
        SMART_HUB_SECRET,
    )
    from app.utils.version import (
        get_version, get_window_title)
except Exception:
    APP_FULL_NAME   = "TASHIL"
    SMART_HUB_HOST  = "0.0.0.0"
    SMART_HUB_PORT  = 7890
    SMART_HUB_SECRET = "TASHIL2026"
    def get_version():      return "1.1.0"
    def get_window_title(p=""): return f"TASHIL — {p}"

# ════════════════════════════════════════════════
# 3. SMART HUB — THREAD DAEMON ARRIÈRE-PLAN
# ════════════════════════════════════════════════
_smart_hub_cache = []   # Fichiers reçus du téléphone
_smart_hub_actif = False


def _demarrer_smart_hub():
    """
    Serveur socket léger — écoute sur port 7890.
    Accepte les connexions du téléphone (Android/iOS)
    et stocke les fichiers reçus dans le cache.
    Fonctionne en daemon thread — jamais sur GUI.
    """
    import socket
    import json
    import base64
    import datetime

    global _smart_hub_actif

    try:
        srv = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM)
        srv.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR, 1)
        srv.bind((SMART_HUB_HOST, SMART_HUB_PORT))
        srv.listen(5)
        srv.settimeout(1.0)
        _smart_hub_actif = True
        print(f"[SmartHub] Écoute sur "
              f"{SMART_HUB_HOST}:{SMART_HUB_PORT}")

        while _smart_hub_actif:
            try:
                conn, addr = srv.accept()
                _traiter_connexion_hub(
                    conn, addr)
            except socket.timeout:
                continue
            except Exception:
                break
    except Exception as ex:
        print(f"[SmartHub] Port occupé "
              f"ou erreur: {ex}")
    finally:
        _smart_hub_actif = False


def _traiter_connexion_hub(conn, addr):
    """Traite une connexion entrante du téléphone."""
    import json
    import base64
    import datetime
    import os

    try:
        conn.settimeout(30)
        data = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            data += chunk
            if len(data) > 50 * 1024 * 1024:
                break  # Max 50 MB

        payload = json.loads(data.decode("utf-8"))
        secret  = payload.get("secret", "")

        if secret != SMART_HUB_SECRET:
            conn.send(b'{"status":"unauthorized"}')
            return

        nom_fichier = payload.get(
            "filename", f"scan_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        contenu_b64 = payload.get("data", "")

        if contenu_b64:
            contenu = base64.b64decode(contenu_b64)
            # Sauvegarder dans dossier cache
            cache_dir = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                "data", "hub_cache")
            os.makedirs(cache_dir, exist_ok=True)
            chemin = os.path.join(
                cache_dir, nom_fichier)
            with open(chemin, "wb") as f:
                f.write(contenu)

            # Ajouter au cache global
            _smart_hub_cache.append({
                "nom":    nom_fichier,
                "chemin": chemin,
                "taille": len(contenu),
                "date":   datetime.datetime.now().isoformat(),
                "source": str(addr[0]),
            })

            conn.send(b'{"status":"ok"}')
            print(f"[SmartHub] Fichier reçu : "
                  f"{nom_fichier} ({len(contenu)} octets)")
        else:
            conn.send(b'{"status":"empty"}')

    except Exception as ex:
        print(f"[SmartHub] Erreur traitement: {ex}")
        try:
            conn.send(b'{"status":"error"}')
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_smart_hub_cache() -> list:
    """Retourne les fichiers reçus via Smart Hub."""
    return list(_smart_hub_cache)


def vider_smart_hub_cache():
    """Vide le cache après utilisation."""
    global _smart_hub_cache
    _smart_hub_cache = []


# ════════════════════════════════════════════════
# 4. TKINTER & FENÊTRE PRINCIPALE
# ════════════════════════════════════════════════
try:
    import customtkinter as ctk
    from app.utils.theme import COULEURS, DIMENSIONS
except Exception as e:
    print(f"[FATAL IMPORT] {e}")
    traceback.print_exc()
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
    global _smart_hub_actif
    _smart_hub_actif = False
    try:
        from app.utils.database import faire_backup
        faire_backup("fermeture")
    except Exception:
        pass
    root.destroy()


root.protocol("WM_DELETE_WINDOW", _fermeture)

# ════════════════════════════════════════════════
# 5. SPLASH SCREEN — MINISTÈRE DE LA SANTÉ
# ════════════════════════════════════════════════

class SplashTASHIL(ctk.CTkToplevel):
    """
    Splash haute performance — Emblème Ministère Santé.
    100% after() — zéro thread GUI.
    """

    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self._cb     = callback
        self._parent = parent
        self._alpha  = 0.0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#060D1A")
        self.resizable(False, False)

        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        w, h = 540, 360
        self.geometry(
            f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self._construire()
        self.after(20,
                   lambda: self._fade(0.0, "in"))

    def _construire(self):
        # Fond principal
        fond = ctk.CTkFrame(
            self, fg_color="#060D1A",
            corner_radius=0,
            border_width=1,
            border_color="#1E3A5F")
        fond.place(x=0, y=0,
                   relwidth=1, relheight=1)

        # Emblème Ministère (simulation géométrique)
        embleme = ctk.CTkFrame(
            fond,
            fg_color="#0A1628",
            corner_radius=60,
            border_width=2,
            border_color="#2563EB",
            width=110, height=110)
        embleme.place(relx=0.5, y=30,
                      anchor="n")
        embleme.pack_propagate(False)

        ctk.CTkLabel(
            embleme, text="⚕",
            font=("Segoe UI", 42),
            text_color="#2563EB"
        ).place(relx=0.5, rely=0.42,
                anchor="center")

        ctk.CTkLabel(
            embleme, text="🇩🇿",
            font=("Segoe UI", 14),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.82,
                anchor="center")

        # République (arabe)
        ctk.CTkLabel(
            fond,
            text=("الجمهورية الجزائرية"
                  " الديمقراطية الشعبية"),
            font=("Segoe UI", 11, "bold"),
            text_color="#94A3B8"
        ).place(relx=0.5, y=152,
                anchor="n")

        ctk.CTkLabel(
            fond,
            text="وزارة الصحة",
            font=("Segoe UI", 10),
            text_color="#64748B"
        ).place(relx=0.5, y=176,
                anchor="n")

        # Séparateur
        ctk.CTkFrame(
            fond, fg_color="#1E3A5F",
            height=1
        ).place(x=60, y=200,
                relwidth=1, width=-120)

        # Nom TASHIL
        ctk.CTkLabel(
            fond, text="TASHIL",
            font=("Segoe UI", 28, "bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, y=212,
                anchor="n")

        ctk.CTkLabel(
            fond,
            text="Smart Health Management System",
            font=("Segoe UI", 10),
            text_color="#3B82F6"
        ).place(relx=0.5, y=248,
                anchor="n")

        # Barre de progression
        self.barre = ctk.CTkProgressBar(
            fond,
            mode="determinate",
            fg_color="#0F1E35",
            progress_color="#2563EB",
            height=4,
            corner_radius=2)
        self.barre.place(
            x=50, y=286,
            relwidth=1, width=-100)
        self.barre.set(0)

        # Label statut
        self.lbl_status = ctk.CTkLabel(
            fond,
            text=f"Initialisation…  "
                 f"{get_full_label()}",
            font=("Segoe UI", 9),
            text_color="#334155")
        self.lbl_status.place(
            relx=0.5, y=298, anchor="n")

        ctk.CTkLabel(
            fond,
            text="COPYRIGHT ILINE TECH 2026 "
                 "BY FERAK ALADDIN",
            font=("Segoe UI", 7),
            text_color="#1E3A5F"
        ).place(relx=0.5, y=336,
                anchor="n")

    def _fade(self, alpha: float, direction: str):
        if direction == "in":
            alpha = min(1.0, alpha + 0.06)
            self.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(
                    16,
                    lambda: self._fade(
                        alpha, "in"))
            else:
                self.after(
                    20,
                    lambda: self._progres(0.0))
        else:
            alpha = max(0.0, alpha - 0.06)
            self.attributes("-alpha", alpha)
            if alpha > 0.0:
                self.after(
                    16,
                    lambda: self._fade(
                        alpha, "out"))
            else:
                self._terminer()

    def _progres(self, val: float):
        if val <= 1.0:
            self.barre.set(val)
            msgs = {
                0.0:  "Initialisation système…",
                0.2:  "Chargement base de données…",
                0.4:  "Vérification intégrité…",
                0.6:  "Démarrage Smart Hub…",
                0.8:  "Préparation interface…",
                1.0:  "Bienvenue dans TASHIL !",
            }
            for seuil in sorted(
                    msgs.keys(), reverse=True):
                if val >= seuil:
                    self.lbl_status.configure(
                        text=f"{msgs[seuil]}  "
                             f"{get_full_label()}")
                    break
            self.after(
                18,
                lambda: self._progres(
                    round(val + 0.012, 3)))
        else:
            self.after(
                300,
                lambda: self._fade(1.0, "out"))

    def _terminer(self):
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


# Import version label pour splash
try:
    from app.utils.version import get_full_label
except Exception:
    def get_full_label(): return "TASHIL v1.1.0"

# ════════════════════════════════════════════════
# 6. AFFICHAGE ERREUR DANS FENÊTRE
# ════════════════════════════════════════════════

def _afficher_erreur(msg: str):
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
        f,
        text="⚠  Erreur TASHIL",
        font=("Segoe UI", 20, "bold"),
        text_color="#EF4444"
    ).place(relx=0.5, rely=0.2,
            anchor="center")
    ctk.CTkLabel(
        f, text=msg[:900],
        font=("Courier", 9),
        text_color="#FCA5A5",
        wraplength=700,
        justify="left"
    ).place(relx=0.5, rely=0.52,
            anchor="center")
    ctk.CTkButton(
        f, text="Quitter",
        fg_color="#DC2626",
        hover_color="#991B1B",
        command=root.destroy,
        width=140, height=40,
        corner_radius=6
    ).place(relx=0.5, rely=0.82,
            anchor="center")


# ════════════════════════════════════════════════
# 7. FONCTIONS DE LANCEMENT
# ════════════════════════════════════════════════

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
            root.title(
                get_window_title(nom))
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
    """Appelé après la fermeture du splash."""
    root.deiconify()
    root.update_idletasks()
    if get_config("activation_done"):
        _lancer_app()
    else:
        _lancer_activation()


# ════════════════════════════════════════════════
# 8. DÉMARRAGE
# ════════════════════════════════════════════════

# Masquer root pendant splash
root.withdraw()

# Lancer Smart Hub en daemon thread
hub_thread = threading.Thread(
    target=_demarrer_smart_hub,
    daemon=True,
    name="SmartHub")
hub_thread.start()

# Afficher splash après 50ms
# (laisse tkinter s'initialiser)
root.after(50, lambda: SplashTASHIL(
    root, callback=_apres_splash))

root.mainloop()
