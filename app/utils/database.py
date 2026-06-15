# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sqlite3
import os
import sys


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'epsp_conge.db')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    NOT NULL UNIQUE,
            nom         TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule        TEXT    NOT NULL UNIQUE,
            nom              TEXT    NOT NULL,
            prenom           TEXT    NOT NULL,
            grade            TEXT    NOT NULL,
            poste            TEXT,
            departement_id   INTEGER NOT NULL REFERENCES departements(id)
                                     ON DELETE RESTRICT,
            est_manip_radio  INTEGER NOT NULL DEFAULT 0,
            actif            INTEGER NOT NULL DEFAULT 1,
            created_at       TEXT    DEFAULT (datetime('now','localtime')),
            updated_at       TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conges_annuels (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id      INTEGER NOT NULL REFERENCES employes(id)
                                    ON DELETE CASCADE,
            annee           INTEGER NOT NULL,
            jours_initiaux  REAL    NOT NULL DEFAULT 0,
            jours_utilises  REAL    NOT NULL DEFAULT 0,
            updated_at      TEXT    DEFAULT (datetime('now','localtime')),
            UNIQUE (employe_id, annee)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mouvements_conge (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id     INTEGER NOT NULL REFERENCES employes(id)
                                   ON DELETE CASCADE,
            conge_id       INTEGER NOT NULL REFERENCES conges_annuels(id)
                                   ON DELETE CASCADE,
            type_conge     TEXT    NOT NULL
                                   CHECK(type_conge IN (
                                       'CONGE_ANNUEL',
                                       'DIS_INTOX',
                                       'SEMESTRE'
                                   )),
            date_debut     TEXT    NOT NULL,
            date_fin       TEXT    NOT NULL,
            nb_jours       REAL    NOT NULL,
            observation    TEXT,
            created_at     TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bordereaux (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            numero         TEXT    NOT NULL UNIQUE,
            date_emission  TEXT    NOT NULL,
            objet          TEXT,
            expediteur     TEXT    DEFAULT 'EPSP ES-SENIA',
            destinataire   TEXT    DEFAULT 'Direction',
            chemin_fichier TEXT,
            created_at     TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bordereau_lignes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            bordereau_id   INTEGER NOT NULL REFERENCES bordereaux(id)
                                   ON DELETE CASCADE,
            ordre          INTEGER NOT NULL,
            categorie      TEXT    NOT NULL
                                   CHECK(categorie IN (
                                       'CONGE_ANNUEL',
                                       'CERTIFICAT_MEDICAL_ARRET',
                                       'CERTIFICAT_MEDICAL_REPRISE',
                                       'DEMANDE_3_JOURS_NAISSANCE',
                                       'DEMANDE_ANNULATION_CONGE'
                                   )),
            designation    TEXT    NOT NULL,
            nb_pieces      INTEGER NOT NULL DEFAULT 1,
            observation    TEXT    DEFAULT 'Pour toutes fins utiles',
            mouvement_id   INTEGER REFERENCES mouvements_conge(id)
                                   ON DELETE SET NULL
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] Base de données initialisée.")
    print(f"[DB] Chemin : {get_db_path()}")


if __name__ == "__main__":
    initialize_database()
