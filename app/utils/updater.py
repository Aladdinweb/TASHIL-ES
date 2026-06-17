# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Système de mise à jour automatique — EPSP ES-SENIA
Vérifie la dernière Release GitHub et propose le téléchargement.
"""
import sys
import os
import threading
import urllib.request
import urllib.error
import json
import shutil
import subprocess
import datetime

GITHUB_API = (
    "https://api.github.com/repos/"
    "Aladdinweb/epsp-conge-manager/releases/latest"
)
VERSION_LOCALE = "1.0"


def obtenir_derniere_version() -> dict | None:
    """
    Interroge l'API GitHub (thread-safe).
    Retourne dict avec 'tag', 'url_exe', 'taille' ou None.
    """
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": "EPSP-CongeManager",
                     "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())

        tag = data.get("tag_name", "")
        assets = data.get("assets", [])
        url_exe = None
        taille  = 0
        for asset in assets:
            if asset["name"].endswith(".exe"):
                url_exe = asset["browser_download_url"]
                taille  = asset.get("size", 0)
                break

        return {
            "tag":     tag,
            "url_exe": url_exe,
            "taille":  taille,
            "notes":   data.get("body", "")[:300],
        }
    except Exception as ex:
        print(f"[Updater] Erreur API : {ex}")
        return None


def version_plus_recente(tag_distant: str) -> bool:
    """Compare le tag GitHub avec la version locale."""
    try:
        def extraire(v):
            parts = v.lstrip("v").split(".")
            return tuple(int(x) for x in parts
                         if x.isdigit())
        return extraire(tag_distant) > extraire(VERSION_LOCALE)
    except Exception:
        return False


def telecharger_et_remplacer(url_exe: str,
                              callback_progres=None,
                              callback_fin=None):
    """
    Télécharge le nouvel .exe dans un thread séparé,
    puis lance un script bat pour remplacer l'exécutable.
    """
    def _worker():
        try:
            if getattr(sys, 'frozen', False):
                exe_actuel = sys.executable
            else:
                exe_actuel = os.path.abspath("main.py")

            dossier    = os.path.dirname(exe_actuel)
            tmp_path   = os.path.join(
                dossier, "_update_temp.exe")
            backup_path = os.path.join(
                dossier, f"_backup_{datetime.date.today()}.exe")

            # Téléchargement avec progression
            def _reporthook(count, block, total):
                if callback_progres and total > 0:
                    pct = min(100,
                              int(count * block * 100 / total))
                    callback_progres(pct)

            urllib.request.urlretrieve(
                url_exe, tmp_path, _reporthook)

            if callback_progres:
                callback_progres(100)

            # Script bat de remplacement (Windows)
            if sys.platform == "win32":
                bat = os.path.join(dossier, "_update.bat")
                with open(bat, "w") as f:
                    f.write(f"""@echo off
timeout /t 2 /nobreak > NUL
move /Y "{exe_actuel}" "{backup_path}"
move /Y "{tmp_path}" "{exe_actuel}"
start "" "{exe_actuel}"
del "%~f0"
""")
                subprocess.Popen(
                    ["cmd", "/c", bat],
                    creationflags=subprocess.CREATE_NO_WINDOW)

            if callback_fin:
                callback_fin(True, "")

        except Exception as ex:
            if callback_fin:
                callback_fin(False, str(ex))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t


def verifier_en_arriere_plan(callback):
    """
    Lance la vérification dans un thread.
    callback(info_dict | None) est appelé en retour.
    """
    def _worker():
        info = obtenir_derniere_version()
        callback(info)

    threading.Thread(target=_worker, daemon=True).start()
