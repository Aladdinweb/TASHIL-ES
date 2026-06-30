# TASHIL: Smart Health Management System
## État du projet — Documentation de traçabilité

**Version actuelle :** v1.1.32+
**Date de dernière mise à jour :** 2026-06-30
**Copyright :** ILINE TECH 2026 BY FERAK ALADDIN
**Dépôt GitHub :** Aladdinweb/epsp-conge-manager

---

## Architecture générale
---

## Règles architecturales immuables

1. **CustomTkinter place()** : `width=`/`height=` UNIQUEMENT dans le
   constructeur du widget, jamais dans `.place()`. Violation = crash
   `ValueError` silencieux sous PyInstaller.

2. **Sidebar** : utilise `pack()` en interne (dans un
   `CTkScrollableFrame`), jamais `place()` avec coordonnées négatives.

3. **Vues principales** : `place(x=0, y=0, relwidth=1, relheight=1)`
   uniquement — jamais `pack(fill="both", expand=True)` sur les
   frames racines (cause écran noir sous PyInstaller).

4. **DB init** : toujours avant `ctk.CTk()`, jamais après.

5. **Refresh interception** : `_modal_actif()` vérifie la présence
   de `CTkToplevel` avant tout rafraîchissement — ne ferme jamais
   un formulaire actif.

6. **FIFO** : déduction toujours sur le reliquat le plus ancien
   en premier. Maladie/Maternité enregistrées SANS déduction.

7. **Crash dump** : toute erreur de boot écrit dans
   `tashil_boot_error.txt` avant `sys.exit(1)`.

---

## Modules fonctionnels

| Module | État | Description |
|---|---|---|
| Dashboard | ✅ Actif | 4 tuiles cliquables, annuaire hiérarchique |
| Employés | ✅ Actif | CRUD, validation Nom/Prénom/Grade/Poly |
| Congés | ✅ Actif | Menu contextuel, FIFO auto |
| Reliquats | ✅ Actif | Matrice multi-années, colonnes dynamiques |
| Bordereau | ✅ Actif | Scan FIFO, export Excel, import document |
| Tableau Service | ✅ Actif | Grille éditable, lock congé auto |
| Administration | ✅ Actif | Messagerie inter-polycliniques |

---

## Signature et déploiement

- **Compilation** : PyInstaller via GitHub Actions (Windows runner)
- **Signature** : signtool.exe avec certificat `SIGNING_CERT_B64`
  (secret GitHub) — optionnel, continue si absent
- **Distribution** : GitHub Releases, tag `v1.1.PATCH`
- **Mise à jour** : téléchargement direct + script `.bat` de
  remplacement automatique

---

## Secrets GitHub requis (optionnels)

| Secret | Usage |
|---|---|
| `SIGNING_CERT_B64` | Certificat .pfx encodé en base64 |
| `SIGNING_CERT_PASSWORD` | Mot de passe du certificat |
| `GITHUB_TOKEN` | Auto-fourni par GitHub Actions |

---

## Historique des corrections critiques

- **v1.1.21-27** : Résolution écran noir (DB init avant tkinter)
- **v1.1.28-31** : Fix ValueError place() (width/height constructeur)
- **v1.1.32** : Sidebar scrollable, Bordereau/Tableau Service rendus
  visibles, badge drapeau sans texte "dz"

---

*Ce fichier doit être mis à jour à chaque changement architectural
majeur pour garantir la continuité du développement.*
