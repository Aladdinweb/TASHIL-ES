# -*- mode: python ; coding: utf-8 -*-
# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os
block_cipher = None
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(BASE_DIR, 'main.py')],
    pathex=[
        BASE_DIR,
        os.path.join(BASE_DIR, 'app'),
        os.path.join(BASE_DIR, 'app', 'utils'),
        os.path.join(BASE_DIR, 'app', 'views'),
        os.path.join(BASE_DIR, 'app', 'reports'),
    ],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'app', 'assets'),
         'app/assets'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL', 'PIL._imagingtk', 'PIL.Image',
        'PIL.ImageTk', 'PIL.ImageDraw',
        'PIL.ImageFont',
        'openpyxl', 'openpyxl.styles',
        'openpyxl.utils', 'openpyxl.writer.excel',
        'sqlite3', 'tkinter', 'tkinter.ttk',
        'tkinter.messagebox', 'tkinter.filedialog',
        'packaging', 'packaging.version',
        'packaging.specifiers', 'darkdetect',
        'hashlib', 'shutil', 'threading',
        'urllib', 'urllib.request',
        'json', 'subprocess',
        'app',
        'app.utils',
        'app.utils.version',
        'app.utils.database',
        'app.utils.theme',
        'app.utils.migration',
        'app.utils.employes_dao',
        'app.utils.conges_dao',
        'app.utils.bordereaux_dao',
        'app.utils.polycliniques_dao',
        'app.utils.deduction_engine',
        'app.utils.updater',
        'app.utils.widgets_import',
        'app.views',
        'app.views.app_principale',
        'app.views.fenetre_principale',
        'app.views.vue_activation',
        'app.views.vue_dashboard',
        'app.views.vue_employes',
        'app.views.vue_conges',
        'app.views.vue_bordereaux',
        'app.views.vue_rollover',
        'app.views.vue_tableau_service',
        'app.views.vue_administration',
        'app.views.widgets',
        'app.views.dialogue_base',
        'app.views.dialogue_employe',
        'app.views.dialogue_conge',
        'app.views.dialogue_solde',
        'app.views.dialogue_confirmation',
        'app.views.dialogue_annulation',
        'app.views.fiche_employe',
        'app.reports',
        'app.reports.bordereau_excel',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy',
        'pandas', 'PyQt5', 'PyQt6',
        'PySide2', 'PySide6', 'wx', 'gi', 'cv2',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries,
    a.zipfiles, a.datas, [],
    name='EPSP_CongeManager',
    debug=False,
    strip=False,
    upx=True,
    icon=os.path.join(
        BASE_DIR, 'app', 'assets', 'epsp_icon.ico'),
    console=False,
    onefile=True,
)
