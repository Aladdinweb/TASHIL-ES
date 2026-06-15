# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion des Employés — EPSP ES-SENIA
(Squelette — sera complété à l'étape 3)
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.widgets_import import (
    BoutonAction, SeparateurH, TitreSection,
    TableauListe, ChampSaisie, MenuDeroulant
)
from app.utils.database import get_connection


class VueEmployes(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre + bouton ajout
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Gestion des Employés",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        BoutonAction(frame_titre, "＋  Nouvel employé",
                     style="succes").pack(side="right")

        SeparateurH(self).pack(fill="x", padx=pad, pady=(0, pad))

        # Barre de recherche + filtre département
        frame_filtres = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtres.pack(fill="x", padx=pad, pady=(0, 12))
        ChampSaisie(frame_filtres,
                    placeholder="🔍  Rechercher par nom ou matricule…",
                    width=320).pack(side="left", padx=(0, 10))

        depts = self._charger_depts()
        MenuDeroulant(frame_filtres,
                      valeurs=["Tous les départements"] + depts,
                      width=220).pack(side="left")

        # Tableau
        cols = [
            ("Matricule",     100),
            ("Nom & Prénom",  200),
            ("Grade",         170),
            ("Département",   160),
            ("Radio",          60),
            ("Statut",         80),
        ]
        self.tableau = TableauListe(self, colonnes=cols)
        self.tableau.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        self._charger_employes()

    def _charger_depts(self) -> list:
        conn = get_connection()
        rows = conn.execute("SELECT nom FROM departements ORDER BY nom").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def _charger_employes(self):
        self.tableau.vider()
        conn = get_connection()
        rows = conn.execute("""
            SELECT e.matricule, e.nom, e.prenom, e.grade,
                   d.code, e.est_manip_radio, e.actif
            FROM employes e
            JOIN departements d ON d.id = e.departement_id
            ORDER BY d.code, e.nom
        """).fetchall()
        conn.close()
        for r in rows:
            nom_complet = f"{r[1]} {r[2]}"
            radio = "✓" if r[5] else "—"
            statut = "Actif" if r[6] else "Inactif"
            self.tableau.ajouter_ligne(
                [r[0], nom_complet, r[3], r[4], radio, statut]
            )

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
