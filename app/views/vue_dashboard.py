# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Tableau de bord — Thread-safe, zéro deadlock.
Watermark drapeau, compteurs cliquables,
annuaire hiérarchique.
"""
import datetime
import threading
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection, get_config
from app.utils.services import HIERARCHIE_GRADES


def _rang_grade(grade: str) -> int:
    try:
        return HIERARCHIE_GRADES.index(grade)
    except ValueError:
        return len(HIERARCHIE_GRADES)


def _charger_stats_thread() -> dict:
    """
    Charge les stats depuis SQLite.
    Appelé dans un thread secondaire.
    """
    try:
        conn = get_connection()
        today  = datetime.date.today().isoformat()
        demain = (datetime.date.today() +
                  datetime.timedelta(days=1)
                  ).isoformat()
        annee  = datetime.date.today().year

        total_emp = conn.execute(
            "SELECT COUNT(*) FROM employes "
            "WHERE actif=1"
        ).fetchone()[0]

        depts = conn.execute("""
            SELECT d.id, d.code, d.nom,
                   COUNT(e.id) as nb
            FROM departements d
            LEFT JOIN employes e
                ON e.departement_id = d.id
                AND e.actif = 1
            GROUP BY d.id
            ORDER BY d.nom
        """).fetchall()

        en_conge = conn.execute("""
            SELECT DISTINCT
                e.id as emp_id,
                e.nom, e.prenom, e.grade,
                d.nom as dept_nom,
                m.date_debut, m.date_fin,
                m.nb_jours,
                COALESCE((
                    SELECT SUM(
                        ca2.jours_initiaux
                        - ca2.jours_utilises)
                    FROM conges_annuels ca2
                    WHERE ca2.employe_id = e.id
                ), 0) as solde_total
            FROM mouvements_conge m
            JOIN employes e
                ON e.id = m.employe_id
            JOIN departements d
                ON d.id = e.departement_id
            WHERE m.date_debut <= ?
              AND m.date_fin   >= ?
              AND e.actif = 1
            ORDER BY m.date_fin ASC
        """, (today, today)).fetchall()

        fin_conge = conn.execute("""
            SELECT DISTINCT
                e.nom, e.prenom, e.grade,
                d.nom as dept_nom,
                m.date_fin, m.date_debut,
                m.nb_jours
            FROM mouvements_conge m
            JOIN employes e
                ON e.id = m.employe_id
            JOIN departements d
                ON d.id = e.departement_id
            WHERE (m.date_fin = ? OR m.date_fin = ?)
              AND m.date_debut <= ?
              AND e.actif = 1
            ORDER BY m.date_fin ASC
        """, (today, demain, today)).fetchall()

        annuaire = conn.execute("""
            SELECT e.id, e.nom, e.prenom,
                   e.grade, e.matricule,
                   d.nom as dept_nom
            FROM employes e
            JOIN departements d
                ON d.id = e.departement_id
            WHERE e.actif = 1
            ORDER BY d.nom, e.nom
        """).fetchall()

        conn.close()

        return {
            "ok":        True,
            "total_emp": total_emp,
            "depts":     [dict(r) for r in depts],
            "en_conge":  [dict(r) for r in en_conge],
            "fin_conge": [dict(r) for r in fin_conge],
            "annuaire":  [dict(r) for r in annuaire],
        }
    except Exception as ex:
        return {"ok": False, "erreur": str(ex)}


class VueDashboard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._timer_id  = None
        self._cases_emp = {}
        self._stats     = None

        # Afficher le skeleton d'abord
        self._afficher_skeleton()
        # Charger les données en arrière-plan
        self.after(50, self._charger_async)

    def _afficher_skeleton(self):
        """Squelette visible immédiatement."""
        pad = DIMENSIONS["padding_page"]

        # Watermark
        self.lbl_wm = ctk.CTkLabel(
            self, text="🇩🇿",
            font=("Segoe UI", 260),
            text_color="#0D1F3C")
        self.lbl_wm.place(
            relx=0.5, rely=0.5,
            anchor="center")

        # En-tête
        fh = ctk.CTkFrame(
            self, fg_color="transparent")
        fh.pack(fill="x", padx=pad,
                pady=(pad, 8))
        poly = get_config("poly_nom") or "ES-SENIA"
        ctk.CTkLabel(
            fh,
            text=f"🇩🇿  {poly}",
            font=("Segoe UI", 12, "bold"),
            text_color=COULEURS["accent_bleu"]
        ).pack(side="left")
        today = datetime.date.today().strftime(
            "%d/%m/%Y")
        ctk.CTkLabel(
            fh,
            text=f"Tableau de bord  •  {today}",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=(14, 0))

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 10))

        # Spinner chargement
        self.frame_loading = ctk.CTkFrame(
            self, fg_color="transparent")
        self.frame_loading.pack(
            expand=True, pady=60)
        ctk.CTkLabel(
            self.frame_loading,
            text="⏳  Chargement des données…",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_secondaire"]
        ).pack()

    def _charger_async(self):
        """Lance le chargement dans un thread."""
        def _worker():
            stats = _charger_stats_thread()
            # Retour au thread principal via after
            self.after(0, lambda s=stats:
                       self._on_stats_loaded(s))

        t = threading.Thread(
            target=_worker, daemon=True)
        t.start()

    def _on_stats_loaded(self, stats: dict):
        """Appelé dans le thread principal."""
        if not stats.get("ok"):
            try:
                self.frame_loading.destroy()
            except Exception:
                pass
            ctk.CTkLabel(
                self,
                text="⚠  Erreur de chargement.\n"
                     f"{stats.get('erreur','')}",
                font=POLICES["corps"],
                text_color=COULEURS["accent_rouge"]
            ).pack(pady=30)
            return

        self._stats = stats
        # Supprimer le spinner
        try:
            self.frame_loading.destroy()
        except Exception:
            pass

        self._afficher_contenu(stats)
        self._demarrer_timer()

    def _afficher_contenu(self, stats: dict):
        pad = DIMENSIONS["padding_page"]

        # ── Alerte retour ─────────────────────────
        nb_fin = len(stats["fin_conge"])
        if nb_fin > 0:
            fa = ctk.CTkFrame(
                self,
                fg_color="#2D1515",
                corner_radius=8,
                border_width=1,
                border_color=COULEURS["accent_rouge"])
            fa.pack(fill="x", padx=pad,
                    pady=(0, 8))
            fal = ctk.CTkFrame(
                fa, fg_color="transparent")
            fal.pack(fill="x", padx=14, pady=8)
            ctk.CTkLabel(
                fal,
                text=f"🔔  {nb_fin} employé(s) "
                     "retournent aujourd'hui "
                     "ou demain !",
                font=POLICES["corps_bold"],
                text_color=COULEURS["accent_rouge"]
            ).pack(side="left")
            ctk.CTkButton(
                fal, text="Voir →",
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

        # ── 4 Cartes ──────────────────────────────
        fc = ctk.CTkFrame(
            self, fg_color="transparent")
        fc.pack(fill="x", padx=pad,
                pady=(0, 10))

        nb_conge = len(stats["en_conge"])

        cartes = [
            ("NOMBRE D'EMPLOYÉS",
             str(stats["total_emp"]),
             "Effectif total actif",
             COULEURS["accent_bleu"],
             lambda: self._popup_depts(
                 stats["depts"])),
            ("SERVICES",
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
            ("⚠  ALERTE FIN DE CONGÉ",
             str(nb_fin),
             "LA REPRISE",
             COULEURS["accent_rouge"],
             lambda: self._popup_fin_conge(
                 stats["fin_conge"])),
        ]

        for i, (titre, val, sous,
                coul, cmd) in enumerate(cartes):
            fc.columnconfigure(i, weight=1)
            c = self._carte(
                fc, titre, val, sous, coul, cmd)
            c.grid(row=0, column=i,
                   padx=5, sticky="nsew")

        # ── Annuaire hiérarchique ─────────────────
        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad,
               pady=(0, 8))

        fann = ctk.CTkFrame(
            self, fg_color="transparent")
        fann.pack(fill="x", padx=pad,
                  pady=(0, 6))
        ctk.CTkLabel(
            fann, text="Les Services",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        ctk.CTkButton(
            fann,
            text="🗑  Suppression Multiple",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"], height=30,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._suppression_multiple
        ).pack(side="right")

        self._construire_annuaire(
            stats["annuaire"])

    def _carte(self, parent, titre, val,
               sous, coul, cmd=None):
        f = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=DIMENSIONS["rayon_carte"],
            border_width=1, border_color=coul,
            cursor="hand2" if cmd else "arrow")

        ctk.CTkFrame(
            f, height=4, fg_color=coul,
            corner_radius=0
        ).pack(fill="x", side="top")

        corps = ctk.CTkFrame(
            f, fg_color="transparent")
        corps.pack(fill="both", expand=True,
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
            for w in ([f, corps] +
                      corps.winfo_children()):
                try:
                    w.bind("<Button-1>",
                           lambda e, c=cmd: c())
                except Exception:
                    pass
        return f

    def _construire_annuaire(self, annuaire: list):
        pad  = DIMENSIONS["padding_page"]
        self._cases_emp = {}

        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(fill="both", expand=True,
                    padx=pad, pady=(0, pad))

        # Grouper par service
        groupes: dict = {}
        for emp in annuaire:
            g = emp.get("dept_nom", "Autre")
            groupes.setdefault(g, []).append(emp)

        for dept, emps in groupes.items():
            # Tri hiérarchique
            emps.sort(key=lambda e:
                      _rang_grade(e.get("grade","")))

            # En-tête groupe
            fg = ctk.CTkFrame(
                scroll,
                fg_color=COULEURS["bg_sidebar"],
                corner_radius=6)
            fg.pack(fill="x", pady=(0, 2))
            fgh = ctk.CTkFrame(
                fg, fg_color="transparent")
            fgh.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(
                fgh, text=f"  {dept}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["accent_bleu"]
            ).pack(side="left")
            ctk.CTkLabel(
                fgh,
                text=f"{len(emps)} agent(s)",
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(side="right")

            # Lignes employés
            for idx, emp in enumerate(emps):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_champ"])
                fe = ctk.CTkFrame(
                    scroll, fg_color=bg,
                    corner_radius=0,
                    cursor="hand2")
                fe.pack(fill="x", pady=1)

                # Checkbox
                var = ctk.BooleanVar(value=False)
                self._cases_emp[emp["id"]] = var
                ctk.CTkCheckBox(
                    fe, text="", variable=var,
                    width=20, height=20,
                    fg_color=COULEURS["accent_rouge"],
                    hover_color="#DC2626",
                    checkmark_color="#FFFFFF",
                    border_color=COULEURS["bordure"]
                ).pack(side="left",
                       padx=(8, 4), pady=5)

                ctk.CTkLabel(
                    fe,
                    text=f"{emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"],
                    width=180, anchor="w"
                ).pack(side="left", padx=(0, 4))

                ctk.CTkLabel(
                    fe,
                    text=emp.get("grade", ""),
                    font=POLICES["tableau"],
                    text_color=COULEURS["texte_secondaire"],
                    width=200, anchor="w"
                ).pack(side="left")

                ctk.CTkLabel(
                    fe,
                    text=emp.get("matricule", ""),
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"],
                    width=90, anchor="w"
                ).pack(side="left")

                def _enter(e, f=fe):
                    f.configure(
                        fg_color=COULEURS["bg_hover"])
                def _leave(e, f=fe, b=bg):
                    f.configure(fg_color=b)

                fe.bind("<Enter>", _enter)
                fe.bind("<Leave>", _leave)
                fe.bind(
                    "<Button-3>",
                    lambda e, ed=emp:
                        self._menu_ctx(e, ed))
                for ch in fe.winfo_children():
                    ch.bind(
                        "<Button-3>",
                        lambda e, ed=emp:
                            self._menu_ctx(e, ed))

    # ── Menu contextuel ───────────────────────────
    def _menu_ctx(self, event, emp: dict):
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        menu.configure(fg_color=COULEURS["bg_carte"])
        menu.geometry(
            f"230x160"
            f"+{event.x_root}+{event.y_root}")

        titre = (f"{emp['nom']} "
                 f"{emp['prenom']}")[:24]
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
             "CONGE_ANNUEL"),
            ("🏥  Congé Maladie",
             "MALADIE"),
            ("👶  Maternité / Autre",
             "MATERNITE"),
            ("🔀  Transférer",
             "TRANSFERT"),
        ]

        for lbl, tp in options:
            def _cmd(t=tp, m=menu, e=emp):
                m.destroy()
                if t == "TRANSFERT":
                    from app.views.dialogue_transfert import (
                        DialogueTransfert)
                    DialogueTransfert(
                        self, emp=e,
                        callback=self.rafraichir)
                else:
                    from app.views.dialogue_conge_rapide import (
                        DialogueCongeRapide)
                    DialogueCongeRapide(
                        self, emp=e,
                        type_conge=t,
                        callback=self.rafraichir)

            ctk.CTkButton(
                menu, text=lbl,
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                font=POLICES["corps"],
                height=30, anchor="w",
                corner_radius=0, command=_cmd
            ).pack(fill="x", padx=4, pady=1)

        menu.bind(
            "<FocusOut>",
            lambda e: menu.destroy())
        menu.focus_set()

    # ── Suppression multiple ──────────────────────
    def _suppression_multiple(self):
        from tkinter import messagebox
        sel = [eid for eid, var
               in self._cases_emp.items()
               if var.get()]
        if not sel:
            messagebox.showwarning(
                "Sélection vide",
                "Cochez au moins un employé.")
            return
        rep = messagebox.askyesno(
            "⚠  Suppression Multiple",
            f"Désactiver {len(sel)} employé(s) ?\n\n"
            "Les données historiques sont conservées.",
            icon="warning")
        if rep:
            conn = get_connection()
            for eid in sel:
                conn.execute(
                    "UPDATE employes SET actif=0 "
                    "WHERE id=?", (eid,))
            conn.commit()
            conn.close()
            self.rafraichir()

    # ── Popups ────────────────────────────────────
    def _popup_depts(self, depts):
        pop = ctk.CTkToplevel(self)
        pop.title("Services")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("420x360")
        pop.grab_set()

        ctk.CTkLabel(
            pop, text="📋  Services & Effectifs",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        sc = ctk.CTkScrollableFrame(
            pop, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        sc.pack(fill="both", expand=True,
                padx=20, pady=(0, 10))

        for d in depts:
            f = ctk.CTkFrame(
                sc, fg_color=COULEURS["bg_champ"],
                corner_radius=6)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(
                f, text=d["nom"],
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left", padx=10, pady=8)
            coul = (COULEURS["accent_vert"]
                    if d["nb"] > 0
                    else COULEURS["texte_discret"])
            ctk.CTkLabel(
                f, text=f"{d['nb']} agent(s)",
                font=POLICES["corps"],
                text_color=coul
            ).pack(side="right", padx=10)

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=pop.destroy
        ).pack(pady=(0, 14))

    def _popup_en_conge(self, en_conge):
        pop = ctk.CTkToplevel(self)
        pop.title("En congé aujourd'hui")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("560x400")
        pop.grab_set()

        today = datetime.date.today().strftime(
            "%d/%m/%Y")
        ctk.CTkLabel(
            pop,
            text=f"🏖  En congé — {today}",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        sc = ctk.CTkScrollableFrame(
            pop, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        sc.pack(fill="both", expand=True,
                padx=20, pady=(0, 10))

        if not en_conge:
            ctk.CTkLabel(
                sc,
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
                    sc, fg_color=bg,
                    corner_radius=6)
                f.pack(fill="x", pady=2)
                ft = ctk.CTkFrame(
                    f, fg_color="transparent")
                ft.pack(fill="x",
                        padx=10, pady=(6, 2))
                ctk.CTkLabel(
                    ft,
                    text=f"👤 {emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"]
                ).pack(side="left")
                solde = emp.get("solde_total", 0)
                coul  = (COULEURS["accent_vert"]
                         if solde > 10
                         else COULEURS["accent_rouge"])
                ctk.CTkLabel(
                    ft,
                    text=f"Solde : {solde:.0f} j",
                    font=POLICES["corps_bold"],
                    text_color=coul
                ).pack(side="right")
                try:
                    d1 = datetime.date.fromisoformat(
                        emp["date_debut"]
                    ).strftime("%d/%m/%Y")
                    d2 = datetime.date.fromisoformat(
                        emp["date_fin"]
                    ).strftime("%d/%m/%Y")
                    txt = f"Du {d1} au {d2}"
                except Exception:
                    txt = ""
                ctk.CTkLabel(
                    f, text=txt,
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(anchor="w",
                       padx=10, pady=(0, 6))

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=pop.destroy
        ).pack(pady=(0, 14))

    def _popup_fin_conge(self, fin_conge):
        pop = ctk.CTkToplevel(self)
        pop.title("⚠  Alertes retour")
        pop.configure(
            fg_color=COULEURS["bg_principal"])
        pop.geometry("540x380")
        pop.grab_set()

        ctk.CTkLabel(
            pop,
            text="🔔  LA REPRISE",
            font=POLICES["sous_titre"],
            text_color=COULEURS["accent_rouge"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        sc = ctk.CTkScrollableFrame(
            pop, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        sc.pack(fill="both", expand=True,
                padx=20, pady=(0, 10))

        today = datetime.date.today()

        if not fin_conge:
            ctk.CTkLabel(
                sc,
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
                    sc, fg_color=bg,
                    corner_radius=6)
                f.pack(fill="x", pady=2)
                ft = ctk.CTkFrame(
                    f, fg_color="transparent")
                ft.pack(fill="x",
                        padx=10, pady=(6, 2))
                ctk.CTkLabel(
                    ft,
                    text=f"👤 {emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"]
                ).pack(side="left")
                try:
                    df = datetime.date.fromisoformat(
                        emp["date_fin"])
                    if df == today:
                        tag  = "RETOUR AUJOURD'HUI"
                        coul = COULEURS["accent_rouge"]
                    else:
                        tag  = "Retour demain"
                        coul = COULEURS["accent_orange"]
                except Exception:
                    tag, coul = "—", "#888"
                ctk.CTkLabel(
                    ft, text=tag,
                    font=POLICES["corps_bold"],
                    text_color=coul
                ).pack(side="right")
                ctk.CTkLabel(
                    f,
                    text=(f"{emp['grade']}  •  "
                          f"{emp['dept_nom']}"),
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(anchor="w",
                       padx=10, pady=(0, 6))

        ctk.CTkButton(
            pop, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=pop.destroy
        ).pack(pady=(0, 14))

    # ── Timer rafraîchissement ────────────────────
    def _demarrer_timer(self):
        self._timer_id = self.after(
            60000, self._auto_refresh)

    def _auto_refresh(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self.rafraichir()

    def rafraichir(self, _=None):
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
        for w in self.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        self._afficher_skeleton()
        self.after(50, self._charger_async)
