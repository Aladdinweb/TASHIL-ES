# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion des Congés & Reliquats — EPSP ES-SENIA
(Squelette — sera complété à l'étape 4)
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.widgets_import import BoutonAction, SeparateurH, TableauListe
from app.utils.database import get_connection


class VueConges(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Reliquats de Congé Annuel",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        BoutonAction(frame_titre, "＋  Enregistrer un congé",
                     style="primaire").pack(side="right")

        SeparateurH(self).pack(fill="x", padx=pad, pady=(0, pad))

        cols = [
            ("Matricule",      100),
            ("Nom & Prénom",   200),
            ("Département",    140),
            ("Année",           70),
            ("Initiaux",        80),
            ("Utilisés",        80),
            ("Restants",        90),
        ]
        self.tableau = TableauListe(self, colonnes=cols)
        self.tableau.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        self._charger_soldes()

    def _charger_soldes(self):
        self.tableau.vider()
        conn = get_connection()
        rows = conn.execute("""
            SELECT e.matricule, e.nom, e.prenom, d.code,
                   ca.annee, ca.jours_initiaux, ca.jours_utilises,
                   (ca.jours_initiaux - ca.jours_utilises) as restant
            FROM conges_annuels ca
            JOIN employes e ON e.id = ca.employe_id
            JOIN departements d ON d.id = e.departement_id
            ORDER BY ca.annee DESC, d.code, e.nom
        """).fetchall()
        conn.close()
        for r in rows:
            restant = r[7]
            self.tableau.ajouter_ligne([
                r[0], f"{r[1]} {r[2]}", r[3],
                str(r[4]), f"{r[5]:.0f}", f"{r[6]:.0f}",
                f"{restant:.0f} j"
            ])

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
