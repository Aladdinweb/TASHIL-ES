# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Moteur de déduction prioritaire — EPSP ES-SENIA
Règle absolue : consommer d'abord les reliquats les plus anciens,
puis seulement l'année courante quand tout reliquat est épuisé.
"""
import datetime
from app.utils.database import get_connection


def obtenir_soldes_ordonnes(employe_id: int,
                             inclure_vides: bool = False) -> list:
    """
    Retourne les soldes d'un employé triés du plus ancien au plus récent.
    Par défaut, n'inclut que les soldes avec des jours restants > 0.
    """
    conn = get_connection()
    sql = """
        SELECT id, annee, jours_initiaux, jours_utilises,
               (jours_initiaux - jours_utilises) AS restant,
               est_reporte, date_cloture
        FROM conges_annuels
        WHERE employe_id = ?
    """
    if not inclure_vides:
        sql += " AND (jours_initiaux - jours_utilises) > 0"
    sql += " ORDER BY annee ASC"
    rows = conn.execute(sql, (employe_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def calculer_plan_deduction(employe_id: int,
                             nb_jours_demandes: float) -> list | None:
    """
    Calcule comment répartir nb_jours_demandes sur les soldes disponibles.
    Priorité : années les plus anciennes en premier.

    Retourne une liste de dicts :
        [{ conge_id, annee, jours_a_deduire }, ...]
    Retourne None si le solde total est insuffisant.
    """
    soldes = obtenir_soldes_ordonnes(employe_id)
    total_disponible = sum(s["restant"] for s in soldes)

    if nb_jours_demandes > total_disponible:
        return None  # Solde insuffisant

    plan = []
    restant_a_deduire = nb_jours_demandes

    for solde in soldes:
        if restant_a_deduire <= 0:
            break
        a_prendre = min(solde["restant"], restant_a_deduire)
        if a_prendre > 0:
            plan.append({
                "conge_id":        solde["id"],
                "annee":           solde["annee"],
                "jours_a_deduire": a_prendre,
            })
            restant_a_deduire -= a_prendre

    return plan


def solde_total_disponible(employe_id: int) -> float:
    """Retourne le total de jours disponibles tous reliquats confondus."""
    soldes = obtenir_soldes_ordonnes(employe_id)
    return sum(s["restant"] for s in soldes)


def enregistrer_conge_prioritaire(employe_id: int,
                                   nb_jours: float,
                                   date_debut: str,
                                   date_fin: str,
                                   type_conge: str = "CONGE_ANNUEL",
                                   observation: str = "") -> list:
    """
    Enregistre une prise de congé en respectant la priorité
    de déduction (anciens reliquats d'abord).

    Retourne la liste des mouvements créés (un par solde impacté).
    Lève ValueError si solde insuffisant.
    """
    plan = calculer_plan_deduction(employe_id, nb_jours)
    if plan is None:
        total = solde_total_disponible(employe_id)
        raise ValueError(
            f"Solde insuffisant : {total:.0f} j disponibles, "
            f"{nb_jours:.0f} j demandés.\n"
            f"(Reliquats tous exercices confondus)"
        )

    conn = get_connection()
    mouvements_crees = []

    for tranche in plan:
        # Insérer le mouvement
        cur = conn.execute("""
            INSERT INTO mouvements_conge
                (employe_id, conge_id, type_conge,
                 date_debut, date_fin, nb_jours, observation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            employe_id,
            tranche["conge_id"],
            type_conge,
            date_debut,
            date_fin,
            tranche["jours_a_deduire"],
            observation or f"Imputation sur reliquat {tranche['annee']}",
        ))

        # Mettre à jour le solde
        conn.execute("""
            UPDATE conges_annuels
            SET jours_utilises = jours_utilises + ?,
                updated_at = datetime('now','localtime')
            WHERE id = ?
        """, (tranche["jours_a_deduire"], tranche["conge_id"]))

        mouvements_crees.append({
            "mouvement_id": cur.lastrowid,
            "conge_id":     tranche["conge_id"],
            "annee":        tranche["annee"],
            "nb_jours":     tranche["jours_a_deduire"],
        })

    conn.commit()
    conn.close()
    return mouvements_crees


# ── Rollover automatique du 1er Mai ──────────────────────────────
def executer_rollover_mai(annee_cloture: int = None,
                           dry_run: bool = False) -> dict:
    """
    Rollover du 1er Mai :
    1. Clôture l'exercice annee_cloture (marque est_reporte=1)
    2. Crée un nouveau solde de 30j pour annee_cloture+1
       si n'existe pas encore.
    3. Les jours restants de annee_cloture deviennent un reliquat
       (ils restent dans conges_annuels avec est_reporte=1).

    dry_run=True : simule sans modifier la base.
    Retourne un dict de rapport.
    """
    import datetime as dt
    if annee_cloture is None:
        annee_cloture = dt.date.today().year
    annee_nouvelle = annee_cloture + 1
    date_exec = dt.date.today().isoformat()

    conn = get_connection()

    # Vérifier si ce rollover a déjà été fait
    deja_fait = conn.execute("""
        SELECT id FROM journal_rollover WHERE annee = ?
    """, (annee_cloture,)).fetchone()

    if deja_fait and not dry_run:
        conn.close()
        return {
            "statut": "deja_fait",
            "annee":  annee_cloture,
            "message": f"Rollover {annee_cloture} déjà exécuté.",
        }

    # Récupérer tous les soldes actifs de annee_cloture
    soldes = conn.execute("""
        SELECT ca.id, ca.employe_id,
               ca.jours_initiaux, ca.jours_utilises,
               (ca.jours_initiaux - ca.jours_utilises) AS restant
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        WHERE ca.annee = ? AND e.actif = 1
          AND ca.est_reporte = 0
    """, (annee_cloture,)).fetchall()

    rapport = {
        "statut":          "dry_run" if dry_run else "ok",
        "annee_cloture":   annee_cloture,
        "annee_nouvelle":  annee_nouvelle,
        "date_exec":       date_exec,
        "nb_employes":     len(soldes),
        "details":         [],
    }

    for s in soldes:
        restant = s["restant"]
        detail = {
            "employe_id":   s["employe_id"],
            "solde_id":     s["id"],
            "restant":      restant,
        }

        if not dry_run:
            # Marquer le solde comme clôturé/reporté
            conn.execute("""
                UPDATE conges_annuels
                SET est_reporte = 1,
                    date_cloture = ?,
                    updated_at = datetime('now','localtime')
                WHERE id = ?
            """, (date_exec, s["id"]))

            # Créer le nouveau solde pour annee_nouvelle
            conn.execute("""
                INSERT OR IGNORE INTO conges_annuels
                    (employe_id, annee, jours_initiaux, jours_utilises)
                VALUES (?, ?, 30, 0)
            """, (s["employe_id"], annee_nouvelle))

            detail["action"] = "reporte_et_nouveau_solde_cree"
        else:
            detail["action"] = "simulation"

        rapport["details"].append(detail)

    if not dry_run:
        # Journaliser le rollover
        conn.execute("""
            INSERT INTO journal_rollover
                (annee, date_exec, nb_employes, details)
            VALUES (?, ?, ?, ?)
        """, (
            annee_cloture,
            date_exec,
            len(soldes),
            str(rapport["details"]),
        ))
        conn.commit()

    conn.close()
    return rapport


def verifier_rollover_necessaire() -> bool:
    """
    Vérifie si le rollover du 1er Mai doit être déclenché
    (date >= 1er mai ET rollover de l'année N-1 pas encore fait).
    """
    import datetime as dt
    aujourd_hui = dt.date.today()
    if aujourd_hui.month < 5:
        return False

    annee_a_cloturer = aujourd_hui.year - 1
    conn = get_connection()
    deja = conn.execute(
        "SELECT id FROM journal_rollover WHERE annee = ?",
        (annee_a_cloturer,)
    ).fetchone()
    conn.close()
    return deja is None
