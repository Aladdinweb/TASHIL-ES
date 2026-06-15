# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Migration base de données — Ajout polycliniques + champ rollover
EPSP ES-SENIA
"""
from app.utils.database import get_connection, initialize_database


POLYCLINIQUES = [
    "POLYCLINIQUE ES SENIA",
    "POLYCLINIQUE AADL AIN BEIDA LOUCIF MABROUK",
    "POLYCLINIQUE AIN BEIDA 1",
    "POLYCLINIQUE AIN BEIDA 2",
    "POLYCLINIQUE SIDI MAAROUF",
    "POLYCLINIQUE SIDI CHAHMI",
    "POLYCLINIQUE EL KERMA",
]


def migrer():
    initialize_database()
    conn = get_connection()
    c = conn.cursor()

    # ── Table polycliniques ───────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS polycliniques (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nom        TEXT    NOT NULL UNIQUE,
            actif      INTEGER NOT NULL DEFAULT 1,
            created_at TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Colonne polyclinique_id sur employes (si absente) ─────────
    colonnes = [r[1] for r in
                c.execute("PRAGMA table_info(employes)").fetchall()]
    if "polyclinique_id" not in colonnes:
        c.execute("""
            ALTER TABLE employes
            ADD COLUMN polyclinique_id INTEGER
                REFERENCES polycliniques(id) ON DELETE SET NULL
        """)
        print("[+] Colonne polyclinique_id ajoutée à employes.")

    # ── Colonne est_reporte sur conges_annuels (rollover flag) ────
    colonnes_ca = [r[1] for r in
                   c.execute("PRAGMA table_info(conges_annuels)").fetchall()]
    if "est_reporte" not in colonnes_ca:
        c.execute("""
            ALTER TABLE conges_annuels
            ADD COLUMN est_reporte INTEGER NOT NULL DEFAULT 0
        """)
        print("[+] Colonne est_reporte ajoutée à conges_annuels.")

    if "date_cloture" not in colonnes_ca:
        c.execute("""
            ALTER TABLE conges_annuels
            ADD COLUMN date_cloture TEXT
        """)
        print("[+] Colonne date_cloture ajoutée à conges_annuels.")

    # ── Table journal_rollover ─────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_rollover (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            annee        INTEGER NOT NULL,
            date_exec    TEXT    NOT NULL,
            nb_employes  INTEGER NOT NULL DEFAULT 0,
            details      TEXT,
            created_at   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    conn.commit()

    # ── Insérer les polycliniques ─────────────────────────────────
    print("\n--- Polycliniques ---")
    for nom in POLYCLINIQUES:
        try:
            c.execute("INSERT INTO polycliniques (nom) VALUES (?)", (nom,))
            conn.commit()
            print(f"  [+] {nom}")
        except Exception:
            print(f"  [=] {nom} déjà présente.")

    conn.close()
    print("\n[OK] Migration terminée.")


if __name__ == "__main__":
    migrer()
