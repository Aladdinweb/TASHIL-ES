# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO — Congés Annuels & Reliquats
Délègue la déduction au moteur prioritaire (deduction_engine).
"""
import datetime
from app.utils.database import get_connection
from app.utils.deduction_engine import (
    enregistrer_conge_prioritaire,
    solde_total_disponible,
    obtenir_soldes_ordonnes,
    calculer_plan_deduction,
)


def calculer_jours(date_debut: str, date_fin: str) -> int:
    d1 = datetime.date.fromisoformat(date_debut)
    d2 = datetime.date.fromisoformat(date_fin)
    if d2 < d1:
        raise ValueError("La date de fin doit être >= à la date de début.")
    return (d2 - d1).days + 1


def lister_soldes(employe_id: int = None,
                  annee: int = None,
                  dept_id: int = None,
                  poly_id: int = None) -> list:
    conn = get_connection()
    sql = """
        SELECT ca.id, ca.employe_id, ca.annee,
               ca.jours_initiaux, ca.jours_utilises,
               (ca.jours_initiaux - ca.jours_utilises) AS restant,
               ca.est_reporte, ca.date_cloture,
               e.matricule, e.nom, e.prenom, e.grade,
               e.est_manip_radio,
               d.id AS dept_id, d.code AS dept_code, d.nom AS dept_nom,
               p.nom AS poly_nom
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        JOIN departements d ON d.id = e.departement_id
        LEFT JOIN polycliniques p ON p.id = e.polyclinique_id
        WHERE e.actif = 1
    """
    params = []
    if employe_id:
        sql += " AND ca.employe_id = ?";  params.append(employe_id)
    if annee:
        sql += " AND ca.annee = ?";       params.append(annee)
    if dept_id:
        sql += " AND d.id = ?";           params.append(dept_id)
    if poly_id:
        sql += " AND e.polyclinique_id = ?"; params.append(poly_id)
    sql += " ORDER BY ca.annee DESC, d.code, e.nom, e.prenom"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_solde(employe_id: int, annee: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT id, employe_id, annee, jours_initiaux, jours_utilises,
               (jours_initiaux - jours_utilises) AS restant,
               est_reporte, date_cloture
        FROM conges_annuels
        WHERE employe_id = ? AND annee = ?
    """, (employe_id, annee)).fetchone()
    conn.close()
    return dict(row) if row else None


def creer_ou_obtenir_solde(employe_id: int,
                            annee: int,
                            jours_initiaux: float = 30.0) -> dict:
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO conges_annuels
            (employe_id, annee, jours_initiaux, jours_utilises)
        VALUES (?, ?, ?, 0)
    """, (employe_id, annee, jours_initiaux))
    conn.commit()
    conn.close()
    return obtenir_solde(employe_id, annee)


def modifier_solde_initial(conge_id: int,
                            nouveaux_jours: float) -> bool:
    conn = get_connection()
    conn.execute("""
        UPDATE conges_annuels
        SET jours_initiaux = ?,
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (nouveaux_jours, conge_id))
    conn.commit()
    conn.close()
    return True


def enregistrer_mouvement(data: dict) -> list:
    """
    Enregistre une prise de congé via le moteur prioritaire.
    Retourne la liste des mouvements créés (un par reliquat impacté).
    """
    return enregistrer_conge_prioritaire(
        employe_id=data["employe_id"],
        nb_jours=data["nb_jours"],
        date_debut=data["date_debut"],
        date_fin=data["date_fin"],
        type_conge=data.get("type_conge", "CONGE_ANNUEL"),
        observation=data.get("observation", ""),
    )


def apercu_deduction(employe_id: int,
                      nb_jours: float) -> list | None:
    """
    Retourne le plan de déduction sans l'exécuter.
    Utile pour l'affichage préalable dans le formulaire.
    """
    return calculer_plan_deduction(employe_id, nb_jours)


def total_disponible(employe_id: int) -> float:
    return solde_total_disponible(employe_id)


def lister_mouvements(employe_id: int = None,
                       conge_id: int = None) -> list:
    conn = get_connection()
    sql = """
        SELECT m.id, m.employe_id, m.conge_id, m.type_conge,
               m.date_debut, m.date_fin, m.nb_jours, m.observation,
               m.created_at,
               e.nom, e.prenom, e.matricule,
               ca.annee
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
        JOIN conges_annuels ca ON ca.id = m.conge_id
        WHERE 1=1
    """
    params = []
    if employe_id:
        sql += " AND m.employe_id = ?"; params.append(employe_id)
    if conge_id:
        sql += " AND m.conge_id = ?";   params.append(conge_id)
    sql += " ORDER BY m.date_debut DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def annuler_mouvement(mouvement_id: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT conge_id, nb_jours FROM mouvements_conge WHERE id = ?",
        (mouvement_id,)
    ).fetchone()
    if not row:
        conn.close()
        return False
    conn.execute("""
        UPDATE conges_annuels
        SET jours_utilises = MAX(0, jours_utilises - ?),
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (row["nb_jours"], row["conge_id"]))
    conn.execute("DELETE FROM mouvements_conge WHERE id = ?",
                 (mouvement_id,))
    conn.commit()
    conn.close()
    return True


def annees_disponibles() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT annee FROM conges_annuels ORDER BY annee DESC"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def lister_employes_actifs() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id, e.matricule, e.nom, e.prenom,
               e.grade, e.est_manip_radio,
               d.code AS dept_code, d.nom AS dept_nom,
               p.nom AS poly_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        LEFT JOIN polycliniques p ON p.id = e.polyclinique_id
        WHERE e.actif = 1
        ORDER BY d.code, e.nom, e.prenom
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
