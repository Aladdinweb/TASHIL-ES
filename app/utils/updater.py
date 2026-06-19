# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Système de mise à jour automatique in-app — EPSP ES-SENIA
Télécharge et remplace l'exécutable sans intervention manuelle.
"""
import sys
import os
import threading
import urllib.request
import urllib.error
import json
import subprocess
import datetime

GITHUB_API = (
    "https://api.github.com/repos/"
    "Aladdinweb/epsp-conge-manager/releases/latest"
)


def obtenir_derniere_version() -> dict | None:
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={
                "User-Agent": "EPSP-CongeManager-Updater",
                "Accept": "application/vnd.github+json",
            })
        with urllib.request.urlopen(
                req, timeout=10) as r:
            data = json.loads(r.read().decode())

        tag     = data.get("tag_name", "")
        assets  = data.get("assets", [])
        url_exe = None
        taille  = 0

        for asset in assets:
            nom = asset.get("name", "")
            if nom.endswith(".exe"):
                url_exe = asset[
                    "browser_download_url"]
                taille  = asset.get("size", 0)
                break

        return {
            "tag":     tag,
            "url_exe": url_exe,
            "taille":  taille,
            "notes":   data.get("body", "")[:400],
        }
    except Exception as ex:
        print(f"[Updater] API error: {ex}")
        return None


def version_plus_recente(tag_distant: str) -> bool:
    from app.utils.version import get_version
    try:
        def _parse(v: str) -> tuple:
            return tuple(
                int(x) for x in
                v.lstrip("v").split(".")
                if x.isdigit())
        return _parse(tag_distant) > _parse(
            get_version())
    except Exception:
        return False


def verifier_en_arriere_plan(callback):
    """
    Vérifie la version en arrière-plan.
    callback(info_dict | None) appelé en retour.
    """
    def _worker():
        info = obtenir_derniere_version()
        callback(info)

    t = threading.Thread(
        target=_worker, daemon=True)
    t.start()


def telecharger_et_remplacer(
        url_exe: str,
        callback_progres=None,
        callback_fin=None):
    """
    Télécharge le nouvel .exe et lance un script
    .bat pour remplacer l'exécutable actuel puis
    redémarrer l'application automatiquement.
    """
    def _worker():
        try:
            # Chemin de l'exécutable actuel
            if getattr(sys, 'frozen', False):
                exe_actuel = sys.executable
            else:
                # Mode dev : simuler
                exe_actuel = os.path.abspath(
                    "EPSP_CongeManager.exe")

            dossier = os.path.dirname(exe_actuel)
            os.makedirs(dossier, exist_ok=True)

            tmp_path = os.path.join(
                dossier, "_update_new.exe")
            bak_path = os.path.join(
                dossier,
                f"_backup_"
                f"{datetime.date.today()}.exe")
            bat_path = os.path.join(
                dossier, "_do_update.bat")

            # Téléchargement avec progression
            def _hook(count, block, total):
                if callback_progres and total > 0:
                    pct = min(
                        100,
                        int(count * block * 100
                            / total))
                    callback_progres(pct)

            urllib.request.urlretrieve(
                url_exe, tmp_path, _hook)

            if callback_progres:
                callback_progres(100)

            if sys.platform != "win32":
                # Non-Windows : juste signaler
                if callback_fin:
                    callback_fin(
                        False,
                        "Mise à jour automatique "
                        "disponible uniquement "
                        "sur Windows.")
                return

            # Script .bat de remplacement atomique
            bat_content = f"""@echo off
title Mise a jour EPSP CongeManager
echo Mise a jour en cours...
timeout /t 2 /nobreak > NUL
:WAIT
tasklist | find /i "EPSP_CongeManager.exe" > NUL
if %errorlevel% == 0 (
    timeout /t 1 /nobreak > NUL
    goto WAIT
)
if exist "{bak_path}" del /f /q "{bak_path}"
move /Y "{exe_actuel}" "{bak_path}"
if %errorlevel% neq 0 (
    echo Erreur backup, annulation.
    move /Y "{tmp_path}" "{exe_actuel}"
    goto END
)
move /Y "{tmp_path}" "{exe_actuel}"
if %errorlevel% neq 0 (
    echo Erreur remplacement.
    move /Y "{bak_path}" "{exe_actuel}"
    goto END
)
echo Mise a jour reussie. Redemarrage...
timeout /t 1 /nobreak > NUL
start "" "{exe_actuel}"
:END
del /f /q "%~f0"
"""
            with open(bat_path, "w",
                      encoding="cp1252") as f:
                f.write(bat_content)

            # Lancer le .bat en arrière-plan
            subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                creationflags=(
                    subprocess.CREATE_NO_WINDOW |
                    subprocess.DETACH_PROCESS),
                close_fds=True)

            if callback_fin:
                callback_fin(True, "")

        except Exception as ex:
            print(f"[Updater] Error: {ex}")
            if callback_fin:
                callback_fin(False, str(ex))

    t = threading.Thread(
        target=_worker, daemon=True)
    t.start()
    return t
