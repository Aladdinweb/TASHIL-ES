# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Onglet RELIQUAT — Soldes multi-années
- Matricule masqué
- Colonnes vides (zéro) masquées automatiquement
"""
import customtkinter as ctk
import datetime
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection


def _charger_reliquats() -> tuple:
    """
    Retourne (liste_employes, annees_actives).
    annees_actives = uniquement les années
    avec au moins un solde > 0.
    """
    conn = get_connection()
    annee_cour = datetime.date.today().year

    emps = conn.execute("""
        SELECT e.id, e.nom, e.prenom,
               e.grade,
               d.nom as service
        FROM employes e
        JOIN departements d
            ON d.id = e.departement_id
        WHERE e.actif = 1
        ORDER BY d.nom, e.nom
    """).fetchall()

    resultats = []
    annees_avec_data = set()

    for e in emps:
        soldes_raw = conn.execute("""
            SELECT annee,
                   (jours_initiaux - jours_utilises)
                   AS restant
            FROM conges_annuels
            WHERE employe_id = ?
              AND (jours_initiaux - jours_utilises) > 0
            ORDER BY annee ASC
        """, (e["id"],)).fetchall()

        soldes = {r["annee"]: r["restant"]
                  for r in soldes_raw}
        total  = sum(soldes.values())

        for a in soldes:
            annees_avec_data.add(a)

        resultats.append({
            "id":      e["id"],
            "nom":     e["nom"],
            "prenom":  e["prenom"],
            "grade":   e["grade"],
            "service": e["service"],
            "soldes":  soldes,
            "total":   total,
        })

    conn.close()

    # Trier les années actives
    annees_actives = sorted(annees_avec_data)
    return resultats, annees_actives


class VueReliquat(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        ft = ctk.CTkFrame(self,
                          fg_color="transparent")
        ft.pack(fill="x", padx=pad,
                pady=(pad, 8))
        ctk.CTkLabel(
            ft,
            text="Reliquats de Congé Annuel",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        ctk.CTkLabel(
            ft,
            text="Soldes multi-années (FIFO)",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(side="left", padx=(10, 0),
               pady=(6, 0))

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 8))

        # Charger données
        data, annees = _charger_reliquats()
        annee_cour = datetime.date.today().year

        # Colonnes dynamiques
        # SANS Matricule, SANS années à zéro
        cols_fixes = [
            ("Nom & Prénom", 200),
            ("Service",      150),
        ]
        cols_annees = [
            (str(a), 75) for a in annees
        ]
        col_total = [("TOTAL", 85)]
        cols = cols_fixes + cols_annees + col_total

        # En-têtes
        frame_head = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=6)
        frame_head.pack(
            fill="x", padx=pad, pady=(0, 2))

        for nom, larg in cols:
            is_old = (nom.isdigit() and
                      int(nom) < annee_cour)
            coul = (COULEURS["accent_orange"]
                    if is_old
                    else COULEURS["texte_secondaire"])
            ctk.CTkLabel(
                frame_head, text=nom,
                font=POLICES["tableau_head"],
                text_color=coul,
                width=larg, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        # Corps scrollable
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.scroll.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, pad))

        if not data:
            ctk.CTkLabel(
                self.scroll,
                text="Aucun employé actif "
                     "avec des reliquats.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=40)
            return

        for idx, emp in enumerate(data):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.scroll, fg_color=bg,
                corner_radius=0,
                cursor="hand2")
            fl.pack(fill="x", pady=1)

            # Nom & Prénom
            ctk.CTkLabel(
                fl,
                text=f"{emp['nom']} "
                     f"{emp['prenom']}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"],
                width=200, anchor="w"
            ).pack(side="left", padx=6, pady=6)

            # Service
            svc = (emp["service"][:18]
                   if emp["service"] else "—")
            ctk.CTkLabel(
                fl, text=svc,
                font=POLICES["tableau"],
                text_color=COULEURS["texte_secondaire"],
                width=150, anchor="w"
            ).pack(side="left", padx=4)

            # Années actives uniquement
            for annee in annees:
                restant = emp["soldes"].get(
                    annee, 0)
                is_old  = annee < annee_cour

                coul = (
                    COULEURS["accent_rouge"]
                    if restant > 0 and is_old
                    else COULEURS["accent_vert"]
                    if restant > 0
                    else COULEURS["texte_discret"])

                ctk.CTkLabel(
                    fl,
                    text=f"{restant:.0f} j",
                    font=POLICES["tableau"],
                    text_color=coul,
                    width=75, anchor="center"
                ).pack(side="left", padx=4)

            # Total
            total = emp["total"]
            coul_t = (
                COULEURS["accent_rouge"]
                if total == 0
                else COULEURS["accent_vert"]
                if total > 15
                else COULEURS["accent_orange"])
            ctk.CTkLabel(
                fl,
                text=f"{total:.0f} j",
                font=POLICES["corps_bold"],
                text_color=coul_t,
                width=85, anchor="center"
            ).pack(side="left", padx=4)

            # Double-clic → fiche
            eid = emp["id"]

            def _dbl(e, i=eid):
                try:
                    from app.views.fiche_employe\
                        import FicheEmploye
                    FicheEmploye(self, emp_id=i)
                except Exception:
                    pass

            for w in ([fl] +
                      fl.winfo_children()):
                w.bind("<Double-Button-1>", _dbl)

    def rafraichir(self, _=None):
        try:
            for w in self.winfo_children():
                w.destroy()
            self._construire()
        except Exception:
            pass
