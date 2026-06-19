# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Migration base de données — EPSP ES-SENIA"""
from app.utils.database import (
    get_connection, initialize_database)

POLYCLINIQUES = [
    ("POLY_01", "POLYCLINIQUE ES SENIA"),
    ("POLY_02",
     "POLYCLINIQUE AADL AIN BEIDA MABROUK LOUCIF"),
    ("POLY_03", "POLYCLINIQUE AIN BEIDA 1"),
    ("POLY_04", "POLYCLINIQUE AIN BEIDA 2"),
    ("POLY_05", "POLYCLINIQUE SIDI MAAROUF"),
    ("POLY_06", "POLYCLINIQUE SIDI CHAHMI"),
    ("POLY_07", "POLYCLINIQUE EL KERMA"),
]

GROUPES_DEFAUT = [
    ("GROUPE_A",   "Groupe A"),
    ("GROUPE_B",   "Groupe B"),
    ("GROUPE_C",   "Groupe C"),
    ("GROUPE_D",   "Groupe D"),
    ("GARDE_POLE", "Garde Pôle"),
    ("ADMIN",      "Administration"),
]


def migrer():
    initialize_database()
    conn = get_connection()
    c    = conn.cursor()

    # Colonnes manquantes employes
    cols = [r[1] for r in c.execute(
        "PRAGMA table_info(employes)").fetchall()]
    alter_map = {
        "polyclinique_id": (
            "ALTER TABLE employes ADD COLUMN "
            "polyclinique_id INTEGER "
            "REFERENCES polycliniques(id) "
            "ON DELETE SET NULL"),
        "annee_entree": (
            "ALTER TABLE employes "
            "ADD COLUMN annee_entree INTEGER"),
        "statut_detach": (
            "ALTER TABLE employes "
            "ADD COLUMN statut_detach TEXT "
            "DEFAULT 'Interne'"),
        "etab_origine": (
            "ALTER TABLE employes "
            "ADD COLUMN etab_origine TEXT"),
        "etab_destination": (
            "ALTER TABLE employes "
            "ADD COLUMN etab_destination TEXT"),
    }
    for col, sql in alter_map.items():
        if col not in cols:
            c.execute(sql)
            print(f"  [+] {col}")

    # Colonnes manquantes conges_annuels
    cols_ca = [r[1] for r in c.execute(
        "PRAGMA table_info(conges_annuels)").fetchall()]
    if "est_reporte" not in cols_ca:
        c.execute("ALTER TABLE conges_annuels "
                  "ADD COLUMN est_reporte INTEGER "
                  "NOT NULL DEFAULT 0")
    if "date_cloture" not in cols_ca:
        c.execute("ALTER TABLE conges_annuels "
                  "ADD COLUMN date_cloture TEXT")

    # Colonne motif mouvements
    cols_mv = [r[1] for r in c.execute(
        "PRAGMA table_info(mouvements_conge)").fetchall()]
    if "motif" not in cols_mv:
        c.execute("ALTER TABLE mouvements_conge "
                  "ADD COLUMN motif TEXT")

    # Colonne code polycliniques
    cols_p = [r[1] for r in c.execute(
        "PRAGMA table_info(polycliniques)").fetchall()]
    if "code" not in cols_p:
        c.execute("ALTER TABLE polycliniques "
                  "ADD COLUMN code TEXT")

    conn.commit()

    # Polycliniques avec codes
    print("\n--- Polycliniques ---")
    for code, nom in POLYCLINIQUES:
        try:
            c.execute(
                "INSERT INTO polycliniques "
                "(code, nom) VALUES (?,?)",
                (code, nom))
            conn.commit()
            print(f"  [+] {code} — {nom}")
        except Exception:
            try:
                c.execute(
                    "UPDATE polycliniques "
                    "SET code=? WHERE nom=?",
                    (code, nom))
                conn.commit()
            except Exception:
                pass
            print(f"  [=] {nom}")

    # Groupes opérationnels
    print("\n--- Groupes ---")
    for code, nom in GROUPES_DEFAUT:
        try:
            c.execute(
                "INSERT INTO departements "
                "(code, nom) VALUES (?,?)",
                (code, nom))
            conn.commit()
            print(f"  [+] {code}")
        except Exception:
            print(f"  [=] {code}")

    conn.close()
    print("\n[OK] Migration terminée.")


if __name__ == "__main__":
    migrer()


def migrer_services():
    """Ajoute la colonne service si absente."""
    from app.utils.database import get_connection
    conn = get_connection()
    c    = conn.cursor()
    cols = [r[1] for r in c.execute(
        "PRAGMA table_info(employes)").fetchall()]
    if "service" not in cols:
        c.execute(
            "ALTER TABLE employes "
            "ADD COLUMN service TEXT "
            "DEFAULT 'Autre'")
        conn.commit()
        print("[+] Colonne service ajoutee")
    conn.close()
