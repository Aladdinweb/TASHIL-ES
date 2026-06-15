# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Tableau de bord — statistiques globales EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.widgets_import import CarteStatistique, SeparateurH, TableauListe
from app.utils.database import get_connection


def _stats_globales() -> dict:
    """Calcule les statistiques pour le tableau de bord."""
    conn = get_connection()
    c = conn.cursor()

    total_emp = c.execute("SELECT COUNT(*) FROM employes WHERE actif=1").fetchone()[0]
    total_dept = c.execute("SELECT COUNT(*) FROM departements").fetchone()[0]

    row = c.execute("""
        SELECT
            SUM(jours_initiaux - jours_utilises) as restants,
            SUM(jours_utilises) as utilises
        FROM conges_annuels
        WHERE annee = strftime('%Y', 'now')
    """).fetchone()
    restants = row[0] or 0
    utilises = row[1] or 0

    soldes_critiques = c.execute("""
        SELECT e.nom, e.prenom, e.grade, ca.annee,
               (ca.jours_initiaux - ca.jours_utilises) as restant
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        WHERE (ca.jours_initiaux - ca.jours_utilises) > 0
          AND ca.annee < strftime('%Y', 'now')
        ORDER BY restant DESC
        LIMIT 8
    """).fetchall()

    conn.close()
    return {
        "total_emp": total_emp,
        "total_dept": total_dept,
        "restants": restants,
        "utilises": utilises,
        "soldes_critiques": soldes_critiques,
    }


class VueDashboard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        stats = _stats_globales()
        pad = DIMENSIONS["padding_page"]

        # ── Titre ────────────────────────────────────────────────
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))

        ctk.CTkLabel(frame_titre,
                     text="Tableau de bord",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")

        ctk.CTkLabel(frame_titre,
                     text="EPSP ES-SENIA — Vue d'ensemble",
                     font=POLICES["corps"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         side="left", padx=(12, 0), pady=(6, 0))

        SeparateurH(self).pack(fill="x", padx=pad, pady=(0, pad))

        # ── Cartes statistiques ───────────────────────────────────
        frame_cartes = ctk.CTkFrame(self, fg_color="transparent")
        frame_cartes.pack(fill="x", padx=pad, pady=(0, pad))

        cartes_data = [
            ("EMPLOYÉS ACTIFS",   str(stats["total_emp"]),
             "Tous services confondus",   COULEURS["accent_bleu"]),
            ("DÉPARTEMENTS",      str(stats["total_dept"]),
             "Unités administratives",   COULEURS["accent_vert"]),
            ("JOURS RESTANTS",    f"{stats['restants']:.0f} j",
             f"Année en cours",          COULEURS["accent_orange"]),
            ("JOURS UTILISÉS",    f"{stats['utilises']:.0f} j",
             "Congés pris cette année",  COULEURS["accent_rouge"]),
        ]

        for i, (titre, val, sous, coul) in enumerate(cartes_data):
            frame_cartes.columnconfigure(i, weight=1)
            carte = CarteStatistique(frame_cartes, titre=titre,
                                     valeur=val, sous_texte=sous,
                                     couleur_accent=coul)
            carte.grid(row=0, column=i, padx=6, pady=0, sticky="nsew")

        # ── Reliquats à traiter ───────────────────────────────────
        SeparateurH(self).pack(fill="x", padx=pad, pady=(0, 16))

        ctk.CTkLabel(self,
                     text="⚠  Reliquats années antérieures non soldés",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["accent_orange"]).pack(
                         anchor="w", padx=pad, pady=(0, 8))

        cols = [
            ("Nom & Prénom",    180),
            ("Grade",           160),
            ("Année",            70),
            ("Jours restants",  120),
        ]
        tableau = TableauListe(self, colonnes=cols)
        tableau.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        if stats["soldes_critiques"]:
            for row in stats["soldes_critiques"]:
                nom_complet = f"{row[0]} {row[1]}"
                couleur_j = (COULEURS["accent_rouge"]
                             if row[4] > 15 else COULEURS["accent_orange"])
                tableau.ajouter_ligne([
                    nom_complet, row[2], str(row[3]), f"{row[4]:.0f} j"
                ])
        else:
            ctk.CTkLabel(tableau,
                         text="✓  Aucun reliquat non soldé — situation nette.",
                         font=POLICES["corps"],
                         text_color=COULEURS["accent_vert"]).pack(pady=20)

    def rafraichir(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._construire()
