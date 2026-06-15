# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO — Polycliniques (branches)
Gestion des polycliniques et association aux employés.
"""
from app.utils.database import get_connection


def lister_polycliniques(actives_seulement: bool = True) -> list:
    conn = get_connection()
    sql = "SELECT id, nom, actif FROM polycliniques"
    if actives_seulement:
        sql += " WHERE actif = 1"
    sql += " ORDER BY nom"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_polyclinique(poly_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, nom, actif FROM polycliniques WHERE id = ?",
        (poly_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def lister_employes_polyclinique(poly_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id, e.matricule, e.nom, e.prenom,
               e.grade, e.poste, e.est_manip_radio, e.actif,
               d.code AS dept_code, d.nom AS dept_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        WHERE e.polyclinique_id = ?
        ORDER BY e.nom, e.prenom
    """, (poly_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def affecter_employe_polyclinique(emp_id: int,
                                   poly_id: int | None) -> bool:
    conn = get_connection()
    conn.execute("""
        UPDATE employes
        SET polyclinique_id = ?,
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (poly_id, emp_id))
    conn.commit()
    conn.close()
    return True


def supprimer_employes_polyclinique(poly_id: int) -> int:
    """
    Suppression logique de TOUS les employés d'une polyclinique.
    Retourne le nombre d'employés désactivés.
    """
    conn = get_connection()
    cur = conn.execute("""
        UPDATE employes
        SET actif = 0,
            updated_at = datetime('now','localtime')
        WHERE polyclinique_id = ? AND actif = 1
    """, (poly_id,))
    count = cur.rowcount
    conn.commit()
    conn.close()
    return count


def transferer_employes(poly_source_id: int,
                         poly_dest_id: int) -> int:
    """
    Transfère tous les employés actifs d'une polyclinique vers une autre.
    Retourne le nombre d'employés transférés.
    """
    conn = get_connection()
    cur = conn.execute("""
        UPDATE employes
        SET polyclinique_id = ?,
            updated_at = datetime('now','localtime')
        WHERE polyclinique_id = ? AND actif = 1
    """, (poly_dest_id, poly_source_id))
    count = cur.rowcount
    conn.commit()
    conn.close()
    return count
