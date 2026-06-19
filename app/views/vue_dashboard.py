# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Tableau de bord — EPSP ES-SENIA
Compteurs cliquables, alerte fin congé, annuaire
hiérarchique, watermark drapeau.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection, get_config

# Hiérarchie des grades pour tri
HIERARCHIE_GRADES = [
    "Médecin Coordinateur",
    "Médecin Chef",
    "Médecin",
    "Médecin Spécialiste",
    "Chirurgien Dentiste",
    "Pharmacien",
    "Biologiste",
    "Psychologue",
    "Manipulateur Radio",
    "Infirmier Anesthésiste",
    "Sage-Femme",
    "Infirmière",
    "Infirmier",
    "Puéricultrice",
    "Aide-Puéricultrice",
    "ATS (Agent Technique de Santé)",
    "Laborantine",
    "Préparatrice en Pharmacie",
    "Opticien",
    "Assistante Médicale",
    "Assistante Sociale",
    "Aide Soignant",
    "Administrateur (ADM)",
    "Agent de Bureau",
    "Agent de Sécurité (OP)",
    "Ambulancier (OP)",
    "Femme de Ménage (OP)",
    "Autre",
]


def _rang_grade(grade: str) -> int:
    try:
        return HIERARCHIE_GRADES.index(grade)
    except ValueError:
        return len(HIERARCHIE_GRADES)


def _charger_stats() -> dict:
    conn = get_connection()
    aujourd_hui = datetime.date.today().isoformat()
    demain = (datetime.date.today() +
              datetime.timedelta(days=1)).isoformat()
    annee = datetime.date.today().year

    total_emp = conn.execute(
        "SELECT COUNT(*) FROM employes "
        "WHERE actif=1"
    ).fetchone()[0]

    depts = conn.execute("""
        SELECT d.code, d.nom, COUNT(e.id) as nb
        FROM departements d
        LEFT JOIN employes e
            ON e.departement_id = d.id AND e.actif=1
        GROUP BY d.id
        ORDER BY d.nom
    """).fetchall()

    en_conge = conn.execute("""
        SELECT DISTINCT e.id, e.nom, e.prenom,
               e.grade, d.code as dept_code,
               m.date_debut, m.date_fin,
               m.nb_jours,
               (SELECT COALESCE(
                   SUM(ca.jours_initiaux
                       - ca.jours_utilises), 0)
                FROM conges_annuels ca
                WHERE ca.employe_id = e.id) as solde_total
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
        JOIN departements d
            ON d.id = e.departement_id
        WHERE m.date_debut <= ?
          AND m.date_fin >= ?
          AND e.actif = 1
        ORDER BY m.date_fin ASC
    """, (aujourd_hui, aujourd_hui)).fetchall()

    fin_conge = conn.execute("""
        SELECT DISTINCT e.nom, e.prenom,
               e.grade, d.code as dept_code,
               m.date_fin, m.date_debut,
               m.nb_jours
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
        JOIN departements d
            ON d.id = e.departement_id
        WHERE (m.date_fin = ? OR m.date_fin = ?)
          AND m.date_debut <= ?
          AND e.actif = 1
        ORDER BY m.date_fin ASC
    """, (aujourd_hui, demain,
          aujourd_hui)).fetchall()

    # Annuaire groupé par département
    annuaire = conn.execute("""
        SELECT e.id, e.nom, e.prenom,
               e.grade, e.matricule,
               d.code as dept_code,
               d.nom as dept_nom
        FROM employes e
        JOIN departements d
            ON d.id = e.departement_id
        WHERE e.actif = 1
        ORDER BY d.nom, e.grade, e.nom
    """).fetchall()

    conn.close()
    return {
        "total_emp":  total_emp,
        "depts":      [dict(r) for r in depts],
        "en_conge":   [dict(r) for r in en_conge],
        "fin_conge":  [dict(r) for r in fin_conge],
        "annuaire":   [dict(r) for r in annuaire],
    }


class VueDashboard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._timer_id  = None
        self._cases_emp = {}  # checkboxes
        self._construire()
        self._demarrer_timer()

    def _construire(self):
        stats = _charger_stats()
        pad   = DIMENSIONS["padding_page"]

        # ── Watermark drapeau (fond) ──────────────
        self.lbl_watermark = ctk.CTkLabel(
            self, text="🇩🇿",
            font=("Segoe UI", 280),
            text_color="#0D1F3C")
        self.lbl_watermark.place(
            relx=0.5, rely=0.5,
            anchor="center")

        # ── En-tête ───────────────────────────────
        frame_head = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_head.pack(
            fill="x", padx=pad,
            pady=(pad, 8))

        # Drapeau + titre poly
        poly = get_config("poly_nom") or "ES-SENIA"
        ctk.CTkLabel(
            frame_head,
            text=f"🇩🇿  {poly}",
            font=("Segoe UI", 13, "bold"),
            text_color=COULEURS["accent_bleu"]
        ).pack(side="left")

        today_str = datetime.date.today().strftime(
            "%d/%m/%Y")
        ctk.CTkLabel(
            frame_head,
            text=f"Tableau de bord  •  {today_str}",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=(16, 0))

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 10))

        # ── Alerte retour ─────────────────────────
        if stats["fin_conge"]:
            nb = len(stats["fin_conge"])
            frame_alerte = ctk.CTkFrame(
                self,
                fg_color="#2D1515",
                corner_radius=8,
                border_width=1,
                border_color=COULEURS["accent_rouge"])
            frame_alerte.pack(
                fill="x", padx=pad,
                pady=(0, 10))
            f_al = ctk.CTkFrame(
                frame_alerte,
                fg_color="transparent")
            f_al.pack(
                fill="x", padx=14, pady=8)
            ctk.CTkLabel(
                f_al,
                text=f"🔔  {nb} employé(s) "
                     f"retournent aujourd'hui "
                     f"ou demain !",
                font=POLICES["corps_bold"],
                text_color=COULEURS["accent_rouge"]
            ).pack(side="left")
            ctk.CTkButton(
                f_al,
                text="Voir →",
                fg_color=COULEURS["accent_rouge"],
                hover_color="#DC2626",
                text_color="#FFFFFF",
                font=POLICES["petit"],
                height=26, width=70,
                corner_radius=4,
                command=lambda:
                    self._popup_fin_conge(
                        stats["fin_conge"])
            ).pack(side="right")

        # ── 4 Cartes statistiques ─────────────────
        frame_cartes = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_cartes.pack(
            fill="x", padx=pad,
            pady=(0, 10))

        nb_conge  = len(stats["en_conge"])
        nb_fin    = len(stats["fin_conge"])

        cartes = [
            ("NOMBRE D'EMPLOYÉS",
             str(stats["total_emp"]),
             "Effectif total actif",
             COULEURS["accent_bleu"],
             lambda: self._popup_depts(
                 stats["depts"])),
            ("DÉPARTEMENTS / GROUPES",
             str(len([d for d in stats["depts"]
                      if d["nb"] > 0])),
             "Cliquer pour la liste",
             COULEURS["accent_vert"],
             lambda: self._popup_depts(
                 stats["depts"])),
            ("EN CONGÉ AUJOURD'HUI",
             str(nb_conge),
             "Cliquer pour la liste",
             COULEURS["accent_orange"],
             lambda: self._popup_en_conge(
                 stats["en_conge"])),
            ("⚠  TIERS D'ALERTE FIN CONGÉ",
             str(nb_fin),
             "Retours aujourd'hui / demain",
             COULEURS["accent_rouge"],
             lambda: self._popup_fin_conge(
                 stats["fin_conge"])),
        ]

        for i, (titre, val, sous,
                coul, cmd) in enumerate(cartes):
            frame_cartes.columnconfigure(i, weight=1)
            c = self._carte(
                frame_cartes, titre,
                val, sous, coul, cmd)
            c.grid(row=0, column=i,
                   padx=5, sticky="nsew")

        # ── Annuaire hiérarchique ─────────────────
        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad,
               pady=(0, 10))

        f_ann_head = ctk.CTkFrame(
            self, fg_color="transparent")
        f_ann_head.pack(
            fill="x", padx=pad,
            pady=(0, 6))

        ctk.CTkLabel(
            f_ann_head,
            text="Annuaire par Groupe",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")

        # Bouton Suppression Multiple
        self.btn_multi_del = ctk.CTkButton(
            f_ann_head,
            text="🗑  Suppression Multiple",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"],
            height=32,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._suppression_multiple)
        self.btn_multi_del.pack(side="right")

        self._construire_annuaire(
            stats["annuaire"])

    def _carte(self, parent, titre, val,
               sous, coul, cmd=None):
        f = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=DIMENSIONS["rayon_carte"],
            border_width=1,
            border_color=coul,
            cursor="hand2" if cmd else "arrow")

        ctk.CTkFrame(
            f, height=4, fg_color=coul,
            corner_radius=0
        ).pack(fill="x", side="top")

        corps = ctk.CTkFrame(
            f, fg_color="transparent")
        corps.pack(
            fill="both", expand=True,
            padx=12, pady=10)

        ctk.CTkLabel(
            corps, text=titre,
            font=POLICES["stat_label"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            corps, text=val,
            font=POLICES["stat_chiffre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            corps, text=sous,
            font=POLICES["petit"],
            text_color=(COULEURS["accent_bleu"]
                        if cmd else
                        COULEURS["texte_discret"])
        ).pack(anchor="w")

        if cmd:
            for w in ([f] +
                      f.winfo_children() + [corps] +
                      corps.winfo_children()):
                try:
                    w.bind("<Button-1>",
                           lambda e: cmd())
                except Exception:
                    pass
        return f

    # ── Annuaire hiérarchique ─────────────────────
    def _construire_annuaire(self, annuaire: list):
        pad = DIMENSIONS["padding_page"]
        self._cases_emp = {}

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, pad))

        # Grouper par département
        groupes: dict = {}
        for emp in annuaire:
            dept = emp["dept_nom"]
            groupes.setdefault(dept, []).append(emp)

        for dept_nom, employes in groupes.items():
            # Trier par hiérarchie
            employes.sort(
                key=lambda e: _rang_grade(
                    e.get("grade", "")))

            # En-tête groupe
            frame_grp = ctk.CTkFrame(
                scroll,
                fg_color=COULEURS["bg_sidebar"],
                corner_radius=6)
            frame_grp.pack(
                fill="x", pady=(0, 2))

            f_grp_head = ctk.CTkFrame(
                frame_grp, fg_color="transparent")
            f_grp_head.pack(
                fill="x", padx=10, pady=6)

            ctk.CTkLabel(
                f_grp_head,
                text=f"  {dept_nom}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["accent_bleu"]
            ).pack(side="left")

            ctk.CTkLabel(
                f_grp_head,
                text=f"{len(employes)} agent(s)",
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(side="right")

            # Lignes employés
            for idx, emp in enumerate(employes):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_champ"])

                frame_emp = ctk.CTkFrame(
                    frame_grp, fg_color=bg,
                    corner_radius=0,
                    cursor="hand2")
                frame_emp.pack(
                    fill="x", pady=1)

                # Checkbox sélection multiple
                var = ctk.BooleanVar(value=False)
                self._cases_emp[emp["id"]] = var
                ctk.CTkCheckBox(
                    frame_emp, text="",
                    variable=var,
                    width=20, height=20,
                    fg_color=COULEURS["accent_rouge"],
                    hover_color="#DC2626",
                    checkmark_color="#FFFFFF",
                    border_color=COULEURS["bordure"]
                ).pack(side="left", padx=(8, 4),
                       pady=5)

                # Nom + grade
                ctk.CTkLabel(
                    frame_emp,
                    text=f"{emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"],
                    width=180, anchor="w"
                ).pack(side="left", padx=(0, 4))

                ctk.CTkLabel(
                    frame_emp,
                    text=emp.get("grade", ""),
                    font=POLICES["tableau"],
                    text_color=COULEURS["texte_secondaire"],
                    width=200, anchor="w"
                ).pack(side="left")

                ctk.CTkLabel(
                    frame_emp,
                    text=emp.get("matricule", ""),
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"],
                    width=90, anchor="w"
                ).pack(side="left")

                # Hover
                eid = emp["id"]
                emp_data = emp

                def on_enter(e, f=frame_emp):
                    f.configure(
                        fg_color=COULEURS["bg_hover"])
                def on_leave(e, f=frame_emp, b=bg):
                    f.configure(fg_color=b)

                frame_emp.bind("<Enter>", on_enter)
                frame_emp.bind("<Leave>", on_leave)

                # Clic droit → menu contextuel
                frame_emp.bind(
                    "<Button-3>",
                    lambda e, ed=emp_data:
                        self._menu_contextuel(e, ed))
                for child in frame_emp.winfo_children():
                    child.bind(
                        "<Button-3>",
                        lambda e, ed=emp_data:
                            self._menu_contextuel(
                                e, ed))

    # ── Menu contextuel clic droit ────────────────
    def _menu_contextuel(self, event, emp: dict):
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        menu.configure(
            fg_color=COULEURS["bg_carte"])
        menu.geometry(
            f"240x170+{event.x_root}+{event.y_root}")

        titre = (f"{emp['nom']} {emp['prenom']}"
                 [:26])
        ctk.CTkLabel(
            menu, text=titre,
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"]
        ).pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkFrame(
            menu, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=8)

        options = [
            ("📅  Congé Annuel",
             lambda: self._conge_rapide(
                 emp, "CONGE_ANNUEL")),
            ("🏥  Congé Maladie",
             lambda: self._conge_rapide(
                 emp, "MALADIE")),
            ("👶  Maternité / Autre",
             lambda: self._conge_rapide(
                 emp, "MATERNITE")),
            ("🔀  Transférer",
             lambda: self._transferer_emp(emp)),
        ]

        for label, cmd in options:
            ctk.CTkButton(
                menu, text=label,
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                font=POLICES["corps"],
                height=32, anchor="w",
                corner_radius=0,
                command=lambda c=cmd, m=menu: (
                    m.destroy(), c())
            ).pack(fill="x", padx=4, pady=1)

        # Fermer si clic ailleurs
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_set()

    def _conge_rapide(self, emp: dict,
                      type_conge: str):
        """Formulaire rapide de saisie de congé."""
        from app.views.dialogue_conge_rapide import (
            DialogueCongeRapide)
        DialogueCongeRapide(
            self, emp=emp, type_conge=type_conge,
            callback=self.rafraichir)

    def _transferer_emp(self, emp: dict):
        from app.views.dialogue_transfert import (
            DialogueTransfert)
        DialogueTransfert(
            self, emp=emp,
            callback=self.rafraichir)

    def _suppression_multiple(self):
        selectionnes = [
            eid for eid, var
            in self._cases_emp.items()
            if var.get()]
        if not selectionnes:
            from tkinter import messagebox
            messagebox.showwarning(
                "Aucune sélection",
                "Cochez au moins un employé.")
            return
        from tkinter import messagebox
        rep = messagebox.askyesno(
            "⚠  Suppression Multiple",
            f"Désactiver {len(selectionnes)} "
            f"employé(s) sélectionné(s) ?\n\n"
            "Les données historiques sont conservées.\n"
            "Cette action est réversible.",
            icon="warning")
        if rep:
            from app.utils.database import (
                get_connection)
            conn = get_connection()
            for eid in selectionnes:
                conn.execute(
                    "UPDATE employes SET actif=0 "
                    "WHERE id=?", (eid,))
            conn.commit()
            conn.close()
            self.rafraichir()

    # ── Popups ────────────────────────────────────
    def _popup_depts(self, depts: list):
        pop = ctk.CTkToplevel(self)
        pop.title("Départements / Groupes")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("420x380")
        pop.grab_set()

        ctk.CTkLabel(
            pop,
            text="📋  Groupes & Effectifs",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        scroll = ctk.CTkScrollableFrame(
            pop,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        scroll.pack(
            fill="both", expand=True,
            padx=20, pady=(0, 10))

        for d in depts:
            f = ctk.CTkFrame(
                scroll,
                fg_color=COULEURS["bg_champ"],
                corner_radius=6)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(
                f, text=d["nom"],
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(
                f,
                text=f"{d['nb']} agent(s)",
                font=POLICES["corps"],
                text_color=(COULEURS["accent_vert"]
                            if d["nb"] > 0
                            else COULEURS["texte_discret"])
            ).pack(side="right", padx=10)

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            command=pop.destroy
        ).pack(pady=(0, 16))

    def _popup_en_conge(self, en_conge: list):
        pop = ctk.CTkToplevel(self)
        pop.title("Employés en congé aujourd'hui")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("580x420")
        pop.grab_set()

        ctk.CTkLabel(
            pop,
            text=f"🏖  En congé — "
                 f"{datetime.date.today().strftime('%d/%m/%Y')}",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        scroll = ctk.CTkScrollableFrame(
            pop,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        scroll.pack(
            fill="both", expand=True,
            padx=20, pady=(0, 10))

        if not en_conge:
            ctk.CTkLabel(
                scroll,
                text="Aucun employé en congé.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
        else:
            for idx, emp in enumerate(en_conge):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_sidebar"])
                f = ctk.CTkFrame(
                    scroll, fg_color=bg,
                    corner_radius=6)
                f.pack(fill="x", pady=2)

                f_top = ctk.CTkFrame(
                    f, fg_color="transparent")
                f_top.pack(
                    fill="x", padx=10, pady=(6, 2))

                ctk.CTkLabel(
                    f_top,
                    text=f"👤 {emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"]
                ).pack(side="left")

                # Solde restant
                solde = emp.get("solde_total", 0)
                coul_s = (COULEURS["accent_vert"]
                          if solde > 10
                          else COULEURS["accent_orange"]
                          if solde > 0
                          else COULEURS["accent_rouge"])
                ctk.CTkLabel(
                    f_top,
                    text=f"Solde : {solde:.0f} j",
                    font=POLICES["corps_bold"],
                    text_color=coul_s
                ).pack(side="right")

                try:
                    d1 = datetime.date.fromisoformat(
                        emp["date_debut"]
                    ).strftime("%d/%m/%Y")
                    d2 = datetime.date.fromisoformat(
                        emp["date_fin"]
                    ).strftime("%d/%m/%Y")
                    dates_txt = f"Du {d1} au {d2}"
                except Exception:
                    dates_txt = ""

                ctk.CTkLabel(
                    f, text=dates_txt,
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(anchor="w", padx=10,
                       pady=(0, 6))

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            command=pop.destroy
        ).pack(pady=(0, 16))

    def _popup_fin_conge(self, fin_conge: list):
        pop = ctk.CTkToplevel(self)
        pop.title("⚠  Alertes Fin de Congé")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("580x400")
        pop.grab_set()

        today = datetime.date.today()
        demain = today + datetime.timedelta(days=1)

        ctk.CTkLabel(
            pop,
            text="🔔  Retours aujourd'hui / demain",
            font=POLICES["sous_titre"],
            text_color=COULEURS["accent_rouge"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        scroll = ctk.CTkScrollableFrame(
            pop,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        scroll.pack(
            fill="both", expand=True,
            padx=20, pady=(0, 10))

        if not fin_conge:
            ctk.CTkLabel(
                scroll,
                text="✅  Aucun retour imminent.",
                font=POLICES["corps"],
                text_color=COULEURS["accent_vert"]
            ).pack(pady=30)
        else:
            for idx, emp in enumerate(fin_conge):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_sidebar"])
                f = ctk.CTkFrame(
                    scroll, fg_color=bg,
                    corner_radius=6)
                f.pack(fill="x", pady=2)

                f_top = ctk.CTkFrame(
                    f, fg_color="transparent")
                f_top.pack(
                    fill="x", padx=10,
                    pady=(6, 2))

                ctk.CTkLabel(
                    f_top,
                    text=f"👤 {emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"]
                ).pack(side="left")

                # Aujourd'hui ou demain?
                try:
                    d_fin = datetime.date.fromisoformat(
                        emp["date_fin"])
                    if d_fin == today:
                        tag  = "RETOUR AUJOURD'HUI"
                        coul = COULEURS["accent_rouge"]
                    else:
                        tag  = "Retour demain"
                        coul = COULEURS["accent_orange"]
                except Exception:
                    tag, coul = "—", COULEURS["texte_discret"]

                ctk.CTkLabel(
                    f_top, text=tag,
                    font=POLICES["corps_bold"],
                    text_color=coul
                ).pack(side="right")

                ctk.CTkLabel(
                    f,
                    text=f"{emp['grade']}  •  "
                         f"{emp['dept_code']}",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(anchor="w", padx=10,
                       pady=(0, 6))

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            command=pop.destroy
        ).pack(pady=(0, 16))

    def _demarrer_timer(self):
        self._timer_id = self.after(
            60000, self._auto_refresh)

    def _auto_refresh(self):
        self.rafraichir()

    def rafraichir(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        for w in self.winfo_children():
            w.destroy()
        self._construire()
        self._demarrer_timer()
