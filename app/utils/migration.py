# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Migration base de données — EPSP ES-SENIA"""
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

    # Colonnes manquantes sur employes
    cols = [r[1] for r in
            c.execute("PRAGMA table_info(employes)").fetchall()]

    if "polyclinique_id" not in cols:
        c.execute("ALTER TABLE employes "
                  "ADD COLUMN polyclinique_id INTEGER "
                  "REFERENCES polycliniques(id) ON DELETE SET NULL")
        print("[+] polyclinique_id ajoutée")

    if "annee_entree" not in cols:
        c.execute("ALTER TABLE employes "
                  "ADD COLUMN annee_entree INTEGER")
        print("[+] annee_entree ajoutée")

    # Colonnes manquantes sur conges_annuels
    cols_ca = [r[1] for r in
               c.execute("PRAGMA table_info(conges_annuels)").fetchall()]
    if "est_reporte" not in cols_ca:
        c.execute("ALTER TABLE conges_annuels "
                  "ADD COLUMN est_reporte INTEGER NOT NULL DEFAULT 0")
        print("[+] est_reporte ajoutée")
    if "date_cloture" not in cols_ca:
        c.execute("ALTER TABLE conges_annuels "
                  "ADD COLUMN date_cloture TEXT")
        print("[+] date_cloture ajoutée")

    # Table journal_rollover
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_rollover (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annee INTEGER NOT NULL,
            date_exec TEXT NOT NULL,
            nb_employes INTEGER NOT NULL DEFAULT 0,
            details TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )""")

    conn.commit()

    # Polycliniques
    print("\n--- Polycliniques ---")
    for nom in POLYCLINIQUES:
        try:
            c.execute(
                "INSERT INTO polycliniques (nom) VALUES (?)",
                (nom,))
            conn.commit()
            print(f"  [+] {nom}")
        except Exception:
            print(f"  [=] {nom} existante")

    conn.close()
    print("\n[OK] Migration terminée.")


if __name__ == "__main__":
    migrer()
