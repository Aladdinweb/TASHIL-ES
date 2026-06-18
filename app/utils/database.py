# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Base de données SQLite — EPSP ES-SENIA
Schéma complet final — reliquat.db
"""
import sqlite3
import os
import sys
import shutil
import datetime
import hashlib


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'reliquat.db')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def faire_backup(raison: str = "auto") -> str | None:
    src = get_db_path()
    if not os.path.exists(src):
        return None
    backup_dir = os.path.join(
        os.path.dirname(src), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    ts  = datetime.datetime.now().strftime(
        "%Y_%m_%d_%H%M%S")
    dst = os.path.join(
        backup_dir, f"backup_{ts}_{raison}.db")
    shutil.copy2(src, dst)
    fichiers = sorted([
        f for f in os.listdir(backup_dir)
        if f.startswith("backup_") and f.endswith(".db")])
    while len(fichiers) > 30:
        os.remove(os.path.join(
            backup_dir, fichiers.pop(0)))
    return dst


def chiffrer_code(code: str) -> str:
    return hashlib.sha256(
        code.encode()).hexdigest()[:32]


def initialize_database():
    conn = get_connection()
    c    = conn.cursor()

    # ── Config système ────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS config (
            cle        TEXT PRIMARY KEY,
            valeur     TEXT,
            updated_at TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Polycliniques ─────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS polycliniques (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            code       TEXT    NOT NULL UNIQUE,
            nom        TEXT    NOT NULL UNIQUE,
            actif      INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Départements ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS departements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    NOT NULL UNIQUE,
            nom         TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Employés ──────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule        TEXT NOT NULL UNIQUE,
            nom              TEXT NOT NULL,
            prenom           TEXT NOT NULL,
            grade            TEXT NOT NULL,
            poste            TEXT,
            departement_id   INTEGER NOT NULL
                REFERENCES departements(id)
                ON DELETE RESTRICT,
            polyclinique_id  INTEGER
                REFERENCES polycliniques(id)
                ON DELETE SET NULL,
            est_manip_radio  INTEGER NOT NULL DEFAULT 0,
            annee_entree     INTEGER,
            statut_detach    TEXT DEFAULT 'Interne'
                CHECK(statut_detach IN (
                    'Interne',
                    'Detache_Entrant',
                    'Detache_Sortant')),
            etab_origine     TEXT,
            etab_destination TEXT,
            actif            INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT
                (datetime('now','localtime')),
            updated_at TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Congés annuels ────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS conges_annuels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id     INTEGER NOT NULL
                REFERENCES employes(id)
                ON DELETE CASCADE,
            annee          INTEGER NOT NULL,
            jours_initiaux REAL    NOT NULL DEFAULT 0,
            jours_utilises REAL    NOT NULL DEFAULT 0,
            est_reporte    INTEGER NOT NULL DEFAULT 0,
            date_cloture   TEXT,
            updated_at     TEXT DEFAULT
                (datetime('now','localtime')),
            UNIQUE (employe_id, annee)
        )""")

    # ── Mouvements ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS mouvements_conge (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id   INTEGER NOT NULL
                REFERENCES employes(id)
                ON DELETE CASCADE,
            conge_id     INTEGER NOT NULL
                REFERENCES conges_annuels(id)
                ON DELETE CASCADE,
            type_conge   TEXT NOT NULL
                CHECK(type_conge IN (
                    'CONGE_ANNUEL','DIS_INTOX',
                    'SEMESTRE','ARRET_TRAVAIL',
                    'REPRISE','NAISSANCE',
                    'MATERNITE','MALADIE',
                    'ANNULATION','ROLLOVER')),
            date_debut   TEXT NOT NULL,
            date_fin     TEXT NOT NULL,
            nb_jours     REAL NOT NULL,
            motif        TEXT,
            observation  TEXT,
            created_at   TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Bordereaux ────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS bordereaux (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            numero         TEXT NOT NULL UNIQUE,
            date_emission  TEXT NOT NULL,
            objet          TEXT,
            expediteur     TEXT DEFAULT 'EPSP ES-SENIA',
            destinataire   TEXT DEFAULT 'Direction',
            chemin_fichier TEXT,
            created_at     TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS bordereau_lignes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            bordereau_id INTEGER NOT NULL
                REFERENCES bordereaux(id)
                ON DELETE CASCADE,
            ordre        INTEGER NOT NULL,
            categorie    TEXT    NOT NULL,
            designation  TEXT    NOT NULL,
            nb_pieces    INTEGER NOT NULL DEFAULT 1,
            observation  TEXT DEFAULT
                'Pour toutes fins utiles',
            mouvement_id INTEGER
                REFERENCES mouvements_conge(id)
                ON DELETE SET NULL
        )""")

    # ── Rollover journal ──────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_rollover (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            annee       INTEGER NOT NULL,
            date_exec   TEXT    NOT NULL,
            nb_employes INTEGER NOT NULL DEFAULT 0,
            details     TEXT,
            created_at  TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Messagerie inter-polycliniques ────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            expediteur   TEXT NOT NULL,
            destinataire TEXT NOT NULL,
            objet        TEXT,
            corps        TEXT,
            piece_jointe TEXT,
            statut       TEXT DEFAULT 'envoye'
                CHECK(statut IN (
                    'envoye','recu','lu')),
            accuse_recu  INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT
                (datetime('now','localtime'))
        )""")

    # ── Tableau de service ────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS tableau_service (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            annee        INTEGER NOT NULL,
            mois         INTEGER NOT NULL,
            employe_id   INTEGER NOT NULL
                REFERENCES employes(id)
                ON DELETE CASCADE,
            jour         INTEGER NOT NULL,
            type_service TEXT NOT NULL DEFAULT 'Repos'
                CHECK(type_service IN (
                    'Matin','Soir','Nuit','Garde',
                    'Repos','Conge','Absent')),
            observation  TEXT,
            created_at   TEXT DEFAULT
                (datetime('now','localtime')),
            UNIQUE(employe_id, annee, mois, jour)
        )""")

    conn.commit()
    conn.close()
    print(f"[OK] DB : {get_db_path()}")


def get_config(cle: str) -> str | None:
    conn = get_connection()
    row  = conn.execute(
        "SELECT valeur FROM config WHERE cle=?",
        (cle,)).fetchone()
    conn.close()
    return row["valeur"] if row else None


def set_config(cle: str, valeur: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO config (cle, valeur, updated_at)
        VALUES (?, ?, datetime('now','localtime'))
        ON CONFLICT(cle) DO UPDATE SET
            valeur=excluded.valeur,
            updated_at=datetime('now','localtime')
    """, (cle, valeur))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
