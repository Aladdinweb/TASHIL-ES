# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
DAO — Bordereaux d'envoi
"""
import datetime
from app.utils.database import get_connection


def prochain_numero(annee: int = None) -> str:
    if annee is None:
        annee = datetime.date.today().year
    conn = get_connection()
    row = conn.execute("""
        SELECT COUNT(*) FROM bordereaux
        WHERE date_emission LIKE ?
    """, (f"%{annee}%",)).fetchone()
    num = (row[0] or 0) + 1
    conn.close()
    return f"{num:03d}/{annee}"


def creer_bordereau(data: dict) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO bordereaux
            (numero, date_emission, objet,
             expediteur, destinataire, chemin_fichier)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["numero"],
        data["date_emission"],
        data.get("objet", "TRANSMISSION DE DOCUMENTS"),
        data.get("expediteur", "EPSP ES-SENIA"),
        data.get("destinataire", "Direction"),
        data.get("chemin_fichier", ""),
    ))
    bord_id = cur.lastrowid

    for ordre, ligne in enumerate(data.get("lignes", []), start=1):
        conn.execute("""
            INSERT INTO bordereau_lignes
                (bordereau_id, ordre, categorie,
                 designation, nb_pieces, observation, mouvement_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            bord_id,
            ordre,
            ligne["categorie"],
            ligne["designation"],
            ligne.get("nb_pieces", 1),
            ligne.get("observation", "Pour toutes fins utiles"),
            ligne.get("mouvement_id"),
        ))

    conn.commit()
    conn.close()
    return bord_id


def lister_bordereaux() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.id, b.numero, b.date_emission, b.objet,
               b.expediteur, b.destinataire, b.chemin_fichier,
               b.created_at,
               COUNT(bl.id) AS nb_pieces
        FROM bordereaux b
        LEFT JOIN bordereau_lignes bl ON bl.bordereau_id = b.id
        GROUP BY b.id
        ORDER BY b.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_bordereau_complet(bord_id: int) -> dict | None:
    conn = get_connection()
    bord = conn.execute(
        "SELECT * FROM bordereaux WHERE id = ?", (bord_id,)
    ).fetchone()
    if not bord:
        conn.close()
        return None
    lignes = conn.execute("""
        SELECT * FROM bordereau_lignes
        WHERE bordereau_id = ?
        ORDER BY ordre
    """, (bord_id,)).fetchall()
    conn.close()
    result = dict(bord)
    result["lignes"] = [dict(l) for l in lignes]
    return result


def supprimer_bordereau(bord_id: int) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM bordereaux WHERE id = ?", (bord_id,))
    conn.commit()
    conn.close()
    return True
