#!/bin/bash
# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
# Script de test build Linux/Termux — EPSP ES-SENIA

echo ""
echo "============================================"
echo " EPSP ES-SENIA — Build Linux/Termux"
echo " COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN"
echo "============================================"
echo ""

# Installer dépendances
echo "[1/3] Installation des dépendances..."
pip install customtkinter openpyxl pillow pyinstaller darkdetect packaging

# Générer icône
echo "[2/3] Génération de l'icône..."
python app/assets/create_icon.py

# Build
echo "[3/3] Compilation..."
pyinstaller epsp_conge.spec \
    --clean \
    --noconfirm \
    --log-level WARN

if [ -f "dist/EPSP_CongeManager" ]; then
    echo ""
    echo "[OK] Build Linux réussi : dist/EPSP_CongeManager"
else
    echo ""
    echo "[INFO] Vérifiez dist/ pour le résultat."
fi
