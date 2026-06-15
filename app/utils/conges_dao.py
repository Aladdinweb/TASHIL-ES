# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO — Congés Annuels & Reliquats
Calculs, enregistrements, et mises à jour des soldes.
"""
import datetime
from app.utils.database import get_connection


# ── Calcul du nombre de jours ouvrables ──────────────────────────
def calculer_jours(date_debut: str, date_fin: str) -> int:
    """
    Retourne le nombre de jours calendaires inclus entre date_debut
    et date_fin (les deux bornes comprises), format YYYY-MM-DD.
    """
    d1 = datetime.date.fromisoformat(date_debut)
    d2 = datetime.date.fromisoformat(date_fin)
    if d2 < d1:
        raise ValueError("La date de fin doit être >= à la date de début.")
    return (d2 - d1).days + 1


# ── Soldes ────────────────────────────────────────────────────────
def lister_soldes(employe_id: int = None,
                  annee: int = None,
                  dept_id: int = None) -> list:
    conn = get_connection()
    sql = """
        SELECT ca.id, ca.employe_id, ca.annee,
               ca.jours_initiaux, ca.jours_utilises,
               (ca.jours_initiaux - ca.jours_utilises) AS restant,
               e.matricule, e.nom, e.prenom, e.grade,
               e.est_manip_radio,
               d.id AS dept_id, d.code AS dept_code, d.nom AS dept_nom
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        JOIN departements d ON d.id = e.departement_id
        WHERE e.actif = 1
    """
    params = []
    if employe_id:
        sql += " AND ca.employe_id = ?"; params.append(employe_id)
    if annee:
        sql += " AND ca.annee = ?";      params.append(annee)
    if dept_id:
        sql += " AND d.id = ?";          params.append(dept_id)
    sql += " ORDER BY ca.annee DESC, d.code, e.nom, e.prenom"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_solde(employe_id: int, annee: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT id, employe_id, annee, jours_initiaux, jours_utilises,
               (jours_initiaux - jours_utilises) AS restant
        FROM conges_annuels
        WHERE employe_id = ? AND annee = ?
    """, (employe_id, annee)).fetchone()
    conn.close()
    return dict(row) if row else None


def creer_ou_obtenir_solde(employe_id: int,
                            annee: int,
                            jours_initiaux: float = 30.0) -> dict:
    """Crée le solde s'il n'existe pas encore, sinon retourne l'existant."""
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


# ── Mouvements (prises de congé) ─────────────────────────────────
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


def enregistrer_mouvement(data: dict) -> int:
    """
    Enregistre une prise de congé et met à jour le solde.
    data doit contenir :
        employe_id, conge_id, type_conge,
        date_debut (YYYY-MM-DD), date_fin (YYYY-MM-DD),
        nb_jours, observation (optionnel)
    """
    conn = get_connection()

    # Vérifier le solde disponible
    row = conn.execute("""
        SELECT jours_initiaux, jours_utilises,
               (jours_initiaux - jours_utilises) AS restant
        FROM conges_annuels WHERE id = ?
    """, (data["conge_id"],)).fetchone()

    if not row:
        conn.close()
        raise ValueError("Solde introuvable.")

    if data["nb_jours"] > row["restant"]:
        conn.close()
        raise ValueError(
            f"Solde insuffisant : {row['restant']:.0f} j disponibles, "
            f"{data['nb_jours']:.0f} j demandés."
        )

    # Insérer le mouvement
    cur = conn.execute("""
        INSERT INTO mouvements_conge
            (employe_id, conge_id, type_conge,
             date_debut, date_fin, nb_jours, observation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["employe_id"],
        data["conge_id"],
        data["type_conge"],
        data["date_debut"],
        data["date_fin"],
        data["nb_jours"],
        data.get("observation", ""),
    ))
    mouvement_id = cur.lastrowid

    # Mettre à jour le solde
    conn.execute("""
        UPDATE conges_annuels
        SET jours_utilises = jours_utilises + ?,
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (data["nb_jours"], data["conge_id"]))

    conn.commit()
    conn.close()
    return mouvement_id


def annuler_mouvement(mouvement_id: int) -> bool:
    """Annule un mouvement et restitue les jours au solde."""
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


# ── Utilitaires ───────────────────────────────────────────────────
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
               d.code AS dept_code, d.nom AS dept_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        WHERE e.actif = 1
        ORDER BY d.code, e.nom, e.prenom
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
