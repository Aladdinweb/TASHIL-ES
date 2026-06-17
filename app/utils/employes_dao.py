# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO — Employés (avec support polyclinique_id)
"""
from app.utils.database import get_connection


def lister_employes(dept_id=None, recherche="") -> list:
    conn = get_connection()
    sql = """
        SELECT e.id, e.matricule, e.nom, e.prenom,
               e.grade, e.poste,
               d.id as dept_id, d.code as dept_code,
               d.nom as dept_nom,
               e.est_manip_radio, e.actif,
               e.polyclinique_id,
               p.nom as poly_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        LEFT JOIN polycliniques p
               ON p.id = e.polyclinique_id
        WHERE 1=1
    """
    params = []
    if dept_id:
        sql += " AND e.departement_id = ?";params.append(dept_id)
    if recherche.strip():
        r = f"%{recherche.strip()}%"
        sql += (" AND (e.nom LIKE ? OR e.prenom LIKE ?"
                " OR e.matricule LIKE ?)")
        params += [r, r, r]
    sql += " ORDER BY d.code, e.nom, e.prenom"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_employe(emp_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT e.id, e.matricule, e.nom, e.prenom,
               e.grade, e.poste, e.departement_id,
               d.code as dept_code, d.nom as dept_nom,
               e.est_manip_radio, e.actif,
               e.polyclinique_id,
               p.nom as poly_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        LEFT JOIN polycliniques p
               ON p.id = e.polyclinique_id
        WHERE e.id = ?
    """, (emp_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def lister_departements() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, code, nom FROM departements ORDER BY nom"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def matricule_existe(matricule: str,
                     exclure_id: int = None) -> bool:
    conn = get_connection()
    if exclure_id:
        row = conn.execute(
            "SELECT id FROM employes "
            "WHERE matricule=? AND id!=?",
            (matricule, exclure_id)).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM employes WHERE matricule=?",
            (matricule,)).fetchone()
    conn.close()
    return row is not None


def modifier_employe(emp_id: int, data: dict) -> bool:
    conn = get_connection()
    conn.execute("""
        UPDATE employes SET
            matricule       = ?,
            nom             = ?,
            prenom          = ?,
            grade           = ?,
            poste           = ?,
            departement_id  = ?,
            polyclinique_id = ?,
            est_manip_radio = ?,
            actif           = ?,
            updated_at      = datetime('now','localtime')
        WHERE id = ?
    """, (
        data["matricule"].strip().upper(),
        data["nom"].strip().upper(),
        data["prenom"].strip(),
        data["grade"].strip(),
        data["poste"].strip(),
        data["departement_id"],
        data.get("polyclinique_id"),
        1 if data.get("est_manip_radio") else 0,
        1 if data.get("actif", True) else 0,
        emp_id,
    ))
    conn.commit()
    conn.close()
    return True


def creer_employe(data: dict) -> int:
    """Fallback simple (sans soldes — utiliser DialogueEmploye)."""
    import datetime
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO employes
            (matricule, nom, prenom, grade, poste,
             departement_id, polyclinique_id,
             est_manip_radio, actif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        data["matricule"].strip().upper(),
        data["nom"].strip().upper(),
        data["prenom"].strip(),
        data["grade"].strip(),
        data["poste"].strip(),
        data["departement_id"],
        data.get("polyclinique_id"),
        1 if data.get("est_manip_radio") else 0,
    ))
    emp_id = cur.lastrowid
    annee  = datetime.date.today().year
    conn.execute("""
        INSERT OR IGNORE INTO conges_annuels
            (employe_id, annee, jours_initiaux, jours_utilises)
        VALUES (?, ?, 30, 0)
    """, (emp_id, annee))
    conn.commit()
    conn.close()
    return emp_id


def supprimer_employe(emp_id: int) -> bool:
    conn = get_connection()
    conn.execute(
        "UPDATE employes SET actif=0, "
        "updated_at=datetime('now','localtime') WHERE id=?",
        (emp_id,))
    conn.commit()
    conn.close()
    return True


def restaurer_employe(emp_id: int) -> bool:
    conn = get_connection()
    conn.execute(
        "UPDATE employes SET actif=1, "
        "updated_at=datetime('now','localtime') WHERE id=?",
        (emp_id,))
    conn.commit()
    conn.close()
    return True
