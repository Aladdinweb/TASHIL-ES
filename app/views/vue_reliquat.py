# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Onglet RELIQUAT — Soldes multi-années par employé
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection
import datetime


def _charger_reliquats() -> list:
    """
    Retourne la liste des employés avec leurs
    soldes par année (2022 → courante).
    """
    conn  = get_connection()
    annee_cour = datetime.date.today().year
    emps  = conn.execute("""
        SELECT e.id, e.nom, e.prenom,
               e.grade, e.matricule,
               d.nom as service
        FROM employes e
        JOIN departements d
            ON d.id = e.departement_id
        WHERE e.actif = 1
        ORDER BY d.nom, e.nom
    """).fetchall()

    resultats = []
    for e in emps:
        soldes_raw = conn.execute("""
            SELECT annee, jours_initiaux,
                   jours_utilises,
                   (jours_initiaux - jours_utilises)
                   AS restant
            FROM conges_annuels
            WHERE employe_id = ?
            ORDER BY annee ASC
        """, (e["id"],)).fetchall()

        soldes = {r["annee"]: r["restant"]
                  for r in soldes_raw}
        total  = sum(soldes.values())

        resultats.append({
            "id":       e["id"],
            "nom":      e["nom"],
            "prenom":   e["prenom"],
            "grade":    e["grade"],
            "matricule":e["matricule"],
            "service":  e["service"],
            "soldes":   soldes,
            "total":    total,
        })

    conn.close()
    return resultats


class VueReliquat(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._annees = list(range(
            2022, datetime.date.today().year + 1))
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
        ).pack(side="left", padx=(12, 0),
               pady=(6, 0))

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 10))

        # En-têtes colonnes dynamiques
        cols = (
            [("Matricule",  88),
             ("Nom & Prénom", 180),
             ("Service", 130)] +
            [(str(a), 68) for a in self._annees] +
            [("TOTAL", 80)]
        )
        self._cols = cols

        frame_head = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=6)
        frame_head.pack(
            fill="x", padx=pad, pady=(0, 2))

        for nom, larg in cols:
            coul = (COULEURS["accent_orange"]
                    if nom.isdigit() and
                    int(nom) < datetime.date.today().year
                    else COULEURS["texte_secondaire"])
            ctk.CTkLabel(
                frame_head, text=nom,
                font=POLICES["tableau_head"],
                text_color=coul,
                width=larg, anchor="w"
            ).pack(side="left", padx=5, pady=7)

        # Corps scrollable
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.scroll.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, pad))

        self._charger()

    def _charger(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        data = _charger_reliquats()

        if not data:
            ctk.CTkLabel(
                self.scroll,
                text="Aucun employé actif.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        annee_cour = datetime.date.today().year

        for idx, emp in enumerate(data):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.scroll, fg_color=bg,
                corner_radius=0,
                cursor="hand2")
            fl.pack(fill="x", pady=1)

            # Colonnes fixes
            for val, (_, larg) in zip(
                [emp["matricule"],
                 f"{emp['nom']} {emp['prenom']}",
                 emp["service"][:16]],
                self._cols[:3]
            ):
                ctk.CTkLabel(
                    fl, text=str(val),
                    font=POLICES["tableau"],
                    text_color=COULEURS["texte_principal"],
                    width=larg, anchor="w"
                ).pack(side="left", padx=5, pady=5)

            # Colonnes années
            for annee in self._annees:
                _, larg = next(
                    (c for c in self._cols
                     if c[0] == str(annee)),
                    (str(annee), 68))
                restant = emp["soldes"].get(annee, 0)
                is_old  = annee < annee_cour
                coul = (
                    COULEURS["accent_rouge"]
                    if restant > 0 and is_old
                    else COULEURS["accent_vert"]
                    if restant > 0
                    else COULEURS["texte_discret"])
                ctk.CTkLabel(
                    fl,
                    text=(f"{restant:.0f} j"
                          if restant > 0 else "—"),
                    font=POLICES["tableau"],
                    text_color=coul,
                    width=larg, anchor="center"
                ).pack(side="left", padx=5)

            # Total
            _, larg_t = self._cols[-1]
            total = emp["total"]
            coul_t = (COULEURS["accent_rouge"]
                      if total == 0
                      else COULEURS["accent_vert"]
                      if total > 15
                      else COULEURS["accent_orange"])
            ctk.CTkLabel(
                fl,
                text=f"{total:.0f} j",
                font=POLICES["corps_bold"],
                text_color=coul_t,
                width=larg_t, anchor="center"
            ).pack(side="left", padx=5)

            # Double-clic → fiche
            eid = emp["id"]

            def _dbl(e, i=eid):
                from app.views.fiche_employe import (
                    FicheEmploye)
                FicheEmploye(self, emp_id=i)

            for w in [fl] + fl.winfo_children():
                w.bind("<Double-Button-1>", _dbl)

    def rafraichir(self):
        try:
            self._charger()
        except Exception:
            pass
