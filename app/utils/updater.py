# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Updater — Téléchargement et remplacement automatique
Thread-safe, zéro blocage GUI.
"""
import sys
import os
import threading
import urllib.request
import json
import subprocess
import datetime

GITHUB_OWNER = "Aladdinweb"
GITHUB_REPO  = "epsp-conge-manager"
GITHUB_API   = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}"
    f"/releases/latest"
)


def obtenir_derniere_version() -> dict | None:
    """
    Interroge l'API GitHub Releases.
    Retourne dict ou None si erreur.
    NE PAS appeler depuis le thread GUI.
    """
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={
                "User-Agent": (
                    "EPSP-CongeManager-Updater/1.0"),
                "Accept": (
                    "application/vnd.github+json"),
            })
        with urllib.request.urlopen(
                req, timeout=12) as resp:
            raw  = resp.read().decode("utf-8")
            data = json.loads(raw)

        tag    = data.get("tag_name", "")
        assets = data.get("assets", [])
        url_exe, taille = None, 0

        for asset in assets:
            if asset.get("name", "").endswith(
                    ".exe"):
                url_exe = asset[
                    "browser_download_url"]
                taille  = asset.get("size", 0)
                break

        return {
            "tag":    tag,
            "url_exe":url_exe,
            "taille": taille,
            "notes":  data.get("body", "")[:400],
        }

    except Exception as ex:
        print(f"[Updater] API error: {ex}")
        return None


def version_plus_recente(tag_distant: str) -> bool:
    """Compare tag GitHub avec version locale."""
    try:
        from app.utils.version import get_version

        def _p(v: str) -> tuple:
            return tuple(
                int(x) for x in
                v.lstrip("v").split(".")
                if x.isdigit())

        return _p(tag_distant) > _p(get_version())
    except Exception:
        return False


def verifier_en_arriere_plan(callback):
    """
    Vérifie la version dans un thread daemon.
    callback(info | None) appelé ensuite.
    GUI doit router via root.after().
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
    Télécharge le nouvel exe dans un thread daemon.
    Crée un script .bat qui :
      1. Attend la fermeture de l'app
      2. Remplace l'exe
      3. Relance automatiquement
    callback_progres(int 0-100) : progression
    callback_fin(bool ok, str err) : résultat
    """
    def _worker():
        tmp_path = None
        bat_path = None
        try:
            # ── Chemins ──────────────────────────
            if getattr(sys, 'frozen', False):
                exe_actuel = sys.executable
            else:
                # Mode dev : dossier courant
                exe_actuel = os.path.join(
                    os.path.dirname(
                        os.path.abspath(__file__)),
                    "..", "..",
                    "EPSP_CongeManager.exe")
                exe_actuel = os.path.abspath(
                    exe_actuel)

            dossier  = os.path.dirname(exe_actuel)
            today    = datetime.date.today().strftime(
                "%Y%m%d")
            tmp_path = os.path.join(
                dossier, "_update_downloading.exe")
            bak_path = os.path.join(
                dossier, f"_bak_{today}.exe")
            bat_path = os.path.join(
                dossier, "_update_launcher.bat")

            os.makedirs(dossier, exist_ok=True)

            # ── Téléchargement ───────────────────
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

            # ── Vérifier que le fichier existe ───
            if not os.path.exists(tmp_path):
                raise FileNotFoundError(
                    "Fichier téléchargé introuvable.")

            taille_dl = os.path.getsize(tmp_path)
            if taille_dl < 1024 * 100:  # < 100 KB
                raise ValueError(
                    f"Fichier trop petit "
                    f"({taille_dl} octets). "
                    "Téléchargement corrompu.")

            if sys.platform != "win32":
                if callback_fin:
                    callback_fin(
                        False,
                        "Mise à jour auto Windows "
                        "uniquement.")
                return

            # ── Script .bat ──────────────────────
            bat = f"""@echo off
chcp 65001 > nul
title EPSP CongeManager - Mise a jour

echo ============================================
echo  EPSP ES-SENIA - Mise a jour automatique
echo ============================================
echo.
echo Attente de la fermeture de l'application...
timeout /t 3 /nobreak > nul

:WAIT_CLOSE
tasklist /fi "IMAGENAME eq EPSP_CongeManager.exe" 2>nul | find /i "EPSP_CongeManager.exe" > nul
if %errorlevel% == 0 (
    timeout /t 1 /nobreak > nul
    goto WAIT_CLOSE
)

echo Application fermee. Installation...

if exist "{bak_path}" (
    del /f /q "{bak_path}" 2>nul
)

if exist "{exe_actuel}" (
    move /Y "{exe_actuel}" "{bak_path}" > nul 2>&1
    if %errorlevel% neq 0 (
        echo ERREUR: Impossible de sauvegarder l'ancien exe.
        echo Restauration...
        goto ERROR
    )
)

move /Y "{tmp_path}" "{exe_actuel}" > nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de placer le nouvel exe.
    if exist "{bak_path}" (
        move /Y "{bak_path}" "{exe_actuel}" > nul 2>&1
    )
    goto ERROR
)

echo.
echo Mise a jour reussie !
echo Redemarrage dans 2 secondes...
timeout /t 2 /nobreak > nul

start "" "{exe_actuel}"
del /f /q "%~f0" 2>nul
exit /b 0

:ERROR
echo.
echo La mise a jour a echoue.
echo Veuillez relancer manuellement.
pause
del /f /q "%~f0" 2>nul
exit /b 1
"""
            with open(bat_path, "w",
                      encoding="utf-8") as f:
                f.write(bat)

            # ── Lancer le .bat ───────────────────
            subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                creationflags=(
                    subprocess.CREATE_NEW_CONSOLE),
                close_fds=True)

            if callback_fin:
                callback_fin(True, "")

        except Exception as ex:
            # Nettoyage fichier temp
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            print(f"[Updater] Error: {ex}")
            if callback_fin:
                callback_fin(False, str(ex))

    t = threading.Thread(
        target=_worker, daemon=True)
    t.start()
    return t
