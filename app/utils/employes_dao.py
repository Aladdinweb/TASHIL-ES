# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO (Data Access Object) — Employés
Toutes les opérations base de données liées aux employés.
"""
from app.utils.database import get_connection


def lister_employes(dept_id: int = None, recherche: str = "") -> list:
    conn = get_connection()
    sql = """
        SELECT e.id, e.matricule, e.nom, e.prenom, e.grade,
               e.poste, d.id as dept_id, d.code as dept_code,
               d.nom as dept_nom, e.est_manip_radio, e.actif
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        WHERE 1=1
    """
    params = []
    if dept_id:
        sql += " AND e.departement_id = ?"
        params.append(dept_id)
    if recherche.strip():
        sql += " AND (e.nom LIKE ? OR e.prenom LIKE ? OR e.matricule LIKE ?)"
        r = f"%{recherche.strip()}%"
        params += [r, r, r]
    sql += " ORDER BY d.code, e.nom, e.prenom"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_employe(emp_id: int) -> dict:
    conn = get_connection()
    row = conn.execute("""
        SELECT e.id, e.matricule, e.nom, e.prenom, e.grade,
               e.poste, e.departement_id, d.code as dept_code,
               d.nom as dept_nom, e.est_manip_radio, e.actif
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
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


def matricule_existe(matricule: str, exclure_id: int = None) -> bool:
    conn = get_connection()
    if exclure_id:
        row = conn.execute(
            "SELECT id FROM employes WHERE matricule=? AND id!=?",
            (matricule, exclure_id)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM employes WHERE matricule=?",
            (matricule,)
        ).fetchone()
    conn.close()
    return row is not None


def creer_employe(data: dict) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO employes
            (matricule, nom, prenom, grade, poste,
             departement_id, est_manip_radio, actif)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        data["matricule"].strip().upper(),
        data["nom"].strip().upper(),
        data["prenom"].strip().capitalize(),
        data["grade"].strip(),
        data["poste"].strip(),
        data["departement_id"],
        1 if data.get("est_manip_radio") else 0,
    ))
    # Créer les soldes de congé pour l'année courante
    import datetime
    annee = datetime.date.today().year
    emp_id = cur.lastrowid
    conn.execute("""
        INSERT OR IGNORE INTO conges_annuels
            (employe_id, annee, jours_initiaux, jours_utilises)
        VALUES (?, ?, 30, 0)
    """, (emp_id, annee))
    conn.commit()
    conn.close()
    return emp_id


def modifier_employe(emp_id: int, data: dict) -> bool:
    conn = get_connection()
    conn.execute("""
        UPDATE employes SET
            matricule      = ?,
            nom            = ?,
            prenom         = ?,
            grade          = ?,
            poste          = ?,
            departement_id = ?,
            est_manip_radio= ?,
            actif          = ?,
            updated_at     = datetime('now','localtime')
        WHERE id = ?
    """, (
        data["matricule"].strip().upper(),
        data["nom"].strip().upper(),
        data["prenom"].strip().capitalize(),
        data["grade"].strip(),
        data["poste"].strip(),
        data["departement_id"],
        1 if data.get("est_manip_radio") else 0,
        1 if data.get("actif") else 0,
        emp_id,
    ))
    conn.commit()
    conn.close()
    return True


def supprimer_employe(emp_id: int) -> bool:
    """Suppression logique (actif → 0)."""
    conn = get_connection()
    conn.execute(
        "UPDATE employes SET actif=0, updated_at=datetime('now','localtime') WHERE id=?",
        (emp_id,)
    )
    conn.commit()
    conn.close()
    return True


def restaurer_employe(emp_id: int) -> bool:
    conn = get_connection()
    conn.execute(
        "UPDATE employes SET actif=1, updated_at=datetime('now','localtime') WHERE id=?",
        (emp_id,)
    )
    conn.commit()
    conn.close()
    return True
