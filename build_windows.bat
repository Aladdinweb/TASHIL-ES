@echo off
REM COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
REM Script de compilation Windows — EPSP ES-SENIA
REM Executer ce fichier sur un PC Windows avec Python installe.

echo.
echo ============================================
echo  EPSP ES-SENIA — Compilation PyInstaller
echo  COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
echo ============================================
echo.

REM Verifier Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Python non trouve. Installez Python 3.10+
    pause
    exit /b 1
)

REM Installer les dependances
echo [1/4] Installation des dependances...
pip install customtkinter openpyxl pillow pyinstaller darkdetect packaging
IF ERRORLEVEL 1 (
    echo [ERREUR] Echec installation dependances.
    pause
    exit /b 1
)

REM Generer l icone
echo [2/4] Generation de l icone...
python app\assets\create_icon.py
IF ERRORLEVEL 1 (
    echo [AVERTISSEMENT] Icone non generee, on continue...
)

REM Nettoyer les anciens builds
echo [3/4] Nettoyage...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Compiler
echo [4/4] Compilation PyInstaller...
pyinstaller epsp_conge.spec --clean --noconfirm
IF ERRORLEVEL 1 (
    echo [ERREUR] Echec de la compilation.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  [OK] Compilation reussie !
echo  Executable : dist\EPSP_CongeManager.exe
echo ============================================
echo.

REM Ouvrir le dossier dist
explorer dist

pause
