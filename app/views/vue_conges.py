# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion des Congés & Reliquats — EPSP ES-SENIA
Soldes par employé/année + historique des mouvements + actions.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import conges_dao
from app.views.dialogue_conge import DialogueConge
from app.views.dialogue_solde import DialogueSolde
from app.views.dialogue_confirmation import DialogueConfirmation


class VueConges(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._solde_sel: dict = None
        self._emp_sel: dict   = None
        self._mouvement_sel_id: int = None
        self._construire()

    # ── Construction ──────────────────────────────────────────────
    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre,
                     text="Reliquats de Congé Annuel",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")

        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, 12))

        # Filtres
        self._construire_filtres(pad)

        # Corps principal : soldes à gauche, détail à droite
        frame_corps = ctk.CTkFrame(self, fg_color="transparent")
        frame_corps.pack(fill="both", expand=True,
                         padx=pad, pady=(0, 0))
        frame_corps.grid_columnconfigure(0, weight=5)
        frame_corps.grid_columnconfigure(1, weight=3)
        frame_corps.grid_rowconfigure(0, weight=1)

        self._construire_tableau_soldes(frame_corps)
        self._construire_panneau_droite(frame_corps)

        # Pied
        self.frame_pied = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=44)
        self.frame_pied.pack(fill="x", side="bottom")
        self.frame_pied.pack_propagate(False)
        self.lbl_pied = ctk.CTkLabel(
            self.frame_pied, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_pied.pack(side="left", padx=pad)

        self._filtrer()

    def _construire_filtres(self, pad):
        frame_f = ctk.CTkFrame(self, fg_color="transparent")
        frame_f.pack(fill="x", padx=pad, pady=(0, 10))

        # Filtre année
        annees_db = conges_dao.annees_disponibles()
        import datetime
        annee_courante = datetime.date.today().year
        toutes_annees = [str(a) for a in annees_db]
        if str(annee_courante) not in toutes_annees:
            toutes_annees.insert(0, str(annee_courante))

        ctk.CTkLabel(frame_f, text="Année :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         side="left", padx=(0, 6))
        self.m_annee = ctk.CTkOptionMenu(
            frame_f, values=["Toutes"] + toutes_annees,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], dropdown_font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=130, height=34,
            command=lambda v: self._filtrer())
        self.m_annee.pack(side="left", padx=(0, 16))
        self.m_annee.set(str(annee_courante))

        # Filtre département
        from app.utils import employes_dao
        self._depts = employes_dao.lister_departements()
        noms_d = (["Tous"] +
                  [f"{d['code']} — {d['nom']}" for d in self._depts])
        ctk.CTkLabel(frame_f, text="Département :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         side="left", padx=(0, 6))
        self.m_dept = ctk.CTkOptionMenu(
            frame_f, values=noms_d,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], dropdown_font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=220, height=34,
            command=lambda v: self._filtrer())
        self.m_dept.pack(side="left", padx=(0, 16))

        self.lbl_compteur = ctk.CTkLabel(
            frame_f, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_compteur.pack(side="left")

    def _construire_tableau_soldes(self, parent):
        cols = [
            ("Matricule",   90),
            ("Nom & Prénom",175),
            ("Dép.",         55),
            ("Année",        60),
            ("Initiaux",     70),
            ("Utilisés",     70),
            ("Restants",     80),
        ]
        self._cols_soldes = cols

        frame_head = ctk.CTkFrame(parent,
                                  fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=8)
        frame_head.grid(row=0, column=0, sticky="new",
                        padx=(0, 8), pady=(0, 2))
        for nom, larg in cols:
            ctk.CTkLabel(frame_head, text=nom,
                         font=POLICES["tableau_head"],
                         text_color=COULEURS["texte_secondaire"],
                         width=larg, anchor="w").pack(
                             side="left", padx=6, pady=8)

        self.frame_soldes = ctk.CTkScrollableFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_soldes.grid(row=0, column=0, sticky="nsew",
                               padx=(0, 8),
                               pady=(40, DIMENSIONS["padding_page"]))

    def _construire_panneau_droite(self, parent):
        self.frame_droite = ctk.CTkFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        self.frame_droite.grid(row=0, column=1, sticky="nsew",
                               pady=(0, DIMENSIONS["padding_page"]))

        ctk.CTkLabel(self.frame_droite,
                     text="Actions",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(self.frame_droite, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        # Info solde sélectionné
        self.lbl_sel_nom = ctk.CTkLabel(
            self.frame_droite,
            text="Sélectionnez un\nemployé dans la liste",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"],
            justify="center", wraplength=180)
        self.lbl_sel_nom.pack(pady=(10, 2))

        self.lbl_sel_info = ctk.CTkLabel(
            self.frame_droite, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"],
            justify="center", wraplength=180)
        self.lbl_sel_info.pack(pady=(0, 10))

        ctk.CTkFrame(self.frame_droite, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        def btn(texte, couleur, hover, cmd, style_txt="#FFFFFF"):
            b = ctk.CTkButton(
                self.frame_droite, text=texte,
                fg_color=couleur, hover_color=hover,
                text_color=style_txt,
                font=POLICES["bouton"], height=34,
                corner_radius=DIMENSIONS["rayon_bouton"],
                state="disabled", command=cmd)
            b.pack(fill="x", padx=14, pady=(0, 8))
            return b

        self.btn_enreg_conge = btn(
            "📅  Enregistrer un congé",
            COULEURS["accent_bleu"], COULEURS["accent_bleu_clair"],
            self._ouvrir_enreg_conge)

        self.btn_modif_solde = btn(
            "✏  Modifier solde initial",
            COULEURS["bg_champ"], COULEURS["bg_hover"],
            self._ouvrir_modif_solde,
            style_txt=COULEURS["texte_principal"])

        self.btn_nouveau_solde = btn(
            "＋  Nouveau solde (autre année)",
            COULEURS["accent_vert"], "#059669",
            self._ouvrir_nouveau_solde)

        ctk.CTkFrame(self.frame_droite, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(4, 10))

        # Historique des mouvements
        ctk.CTkLabel(self.frame_droite,
                     text="Historique des prises",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         anchor="w", padx=14)

        self.frame_historique = ctk.CTkScrollableFrame(
            self.frame_droite,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=6,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_historique.pack(fill="both", expand=True,
                                   padx=14, pady=(6, 14))

        self.lbl_historique_vide = ctk.CTkLabel(
            self.frame_historique,
            text="Aucun mouvement.",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"])
        self.lbl_historique_vide.pack(pady=16)

    # ── Filtrage ──────────────────────────────────────────────────
    def _filtrer(self):
        annee_sel = self.m_annee.get()
        dept_sel  = self.m_dept.get()

        annee  = int(annee_sel) if annee_sel != "Toutes" else None
        dept_id = None
        if dept_sel and dept_sel != "Tous":
            code = dept_sel.split("—")[0].strip()
            for d in self._depts:
                if d["code"] == code:
                    dept_id = d["id"]
                    break

        soldes = conges_dao.lister_soldes(annee=annee, dept_id=dept_id)
        self._afficher_soldes(soldes)
        self.lbl_compteur.configure(text=f"{len(soldes)} solde(s)")

    def _afficher_soldes(self, soldes: list):
        for w in self.frame_soldes.winfo_children():
            w.destroy()
        self._solde_sel = None
        self._emp_sel   = None
        self._reinitialiser_droite()

        if not soldes:
            ctk.CTkLabel(self.frame_soldes,
                         text="Aucun solde trouvé.",
                         font=POLICES["corps"],
                         text_color=COULEURS["texte_discret"]).pack(pady=30)
            return

        for idx, s in enumerate(soldes):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0 else COULEURS["bg_champ"])
            restant = s["restant"]
            couleur_r = (COULEURS["accent_vert"] if restant > 10
                         else COULEURS["accent_orange"] if restant > 0
                         else COULEURS["accent_rouge"])

            frame_l = ctk.CTkFrame(self.frame_soldes,
                                   fg_color=bg, corner_radius=0,
                                   cursor="hand2")
            frame_l.pack(fill="x", pady=1)

            valeurs = [
                s["matricule"],
                f"{s['nom']} {s['prenom']}",
                s["dept_code"],
                str(s["annee"]),
                f"{s['jours_initiaux']:.0f}",
                f"{s['jours_utilises']:.0f}",
                f"{restant:.0f} j",
            ]
            for i, (_, larg) in enumerate(self._cols_soldes):
                coul = (couleur_r if i == 6
                        else COULEURS["texte_principal"])
                ctk.CTkLabel(frame_l, text=valeurs[i],
                             font=POLICES["tableau"],
                             text_color=coul,
                             width=larg, anchor="w").pack(
                                 side="left", padx=6, pady=6)

            def on_enter(e, f=frame_l):
                f.configure(fg_color=COULEURS["bg_hover"])
            def on_leave(e, f=frame_l, b=bg):
                f.configure(fg_color=b)
            def on_click(e, sd=s):
                self._selectionner_solde(sd)

            for widget in [frame_l] + frame_l.winfo_children():
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)

    # ── Sélection ─────────────────────────────────────────────────
    def _selectionner_solde(self, solde: dict):
        self._solde_sel = solde
        self._emp_sel = {
            "id":            solde["employe_id"],
            "nom":           solde["nom"],
            "prenom":        solde["prenom"],
            "grade":         solde.get("grade", ""),
            "est_manip_radio": solde.get("est_manip_radio", 0),
            "dept_code":     solde["dept_code"],
        }
        restant = solde["restant"]
        self.lbl_sel_nom.configure(
            text=f"{solde['nom']}\n{solde['prenom']}",
            text_color=COULEURS["texte_principal"])
        self.lbl_sel_info.configure(
            text=f"{solde['dept_code']} — {solde['annee']}\n"
                 f"Restant : {restant:.0f} j")
        self.btn_enreg_conge.configure(
            state="normal" if restant > 0 else "disabled")
        self.btn_modif_solde.configure(state="normal")
        self.btn_nouveau_solde.configure(state="normal")
        self.lbl_pied.configure(
            text=f"Sélectionné : {solde['matricule']} — "
                 f"{solde['nom']} {solde['prenom']} / {solde['annee']}")
        self._charger_historique(solde["id"])

    def _reinitialiser_droite(self):
        self.lbl_sel_nom.configure(
            text="Sélectionnez un\nemployé dans la liste",
            text_color=COULEURS["texte_secondaire"])
        self.lbl_sel_info.configure(text="")
        self.btn_enreg_conge.configure(state="disabled")
        self.btn_modif_solde.configure(state="disabled")
        self.btn_nouveau_solde.configure(state="disabled")
        self.lbl_pied.configure(text="")
        self._vider_historique()

    def _charger_historique(self, conge_id: int):
        self._vider_historique()
        mouvements = conges_dao.lister_mouvements(conge_id=conge_id)
        if not mouvements:
            self.lbl_historique_vide.configure(text="Aucun mouvement.")
            self.lbl_historique_vide.pack(pady=16)
            return

        types_labels = {
            "CONGE_ANNUEL": ("📅", COULEURS["accent_bleu"]),
            "DIS_INTOX":    ("⚡", COULEURS["accent_orange"]),
            "SEMESTRE":     ("🔄", COULEURS["accent_vert"]),
        }

        for m in mouvements:
            icone, coul = types_labels.get(
                m["type_conge"], ("📅", COULEURS["accent_bleu"]))
            frame_m = ctk.CTkFrame(self.frame_historique,
                                   fg_color=COULEURS["bg_carte"],
                                   corner_radius=6)
            frame_m.pack(fill="x", pady=3)

            f_top = ctk.CTkFrame(frame_m, fg_color="transparent")
            f_top.pack(fill="x", padx=8, pady=(6, 2))

            ctk.CTkLabel(f_top, text=f"{icone} {m['nb_jours']:.0f} j",
                         font=POLICES["corps_bold"],
                         text_color=coul).pack(side="left")

            # Bouton annuler le mouvement
            mid = m["id"]
            ctk.CTkButton(
                f_top, text="✕",
                fg_color="transparent",
                hover_color=COULEURS["accent_rouge"],
                text_color=COULEURS["texte_discret"],
                font=POLICES["petit"],
                width=22, height=22,
                corner_radius=4,
                command=lambda i=mid: self._annuler_mouvement(i)
            ).pack(side="right")

            # Formater les dates
            try:
                from datetime import date
                d1 = date.fromisoformat(m["date_debut"])
                d2 = date.fromisoformat(m["date_fin"])
                dates_txt = (f"Du {d1.strftime('%d/%m/%Y')}\n"
                             f"au {d2.strftime('%d/%m/%Y')}")
            except Exception:
                dates_txt = f"{m['date_debut']} → {m['date_fin']}"

            ctk.CTkLabel(frame_m, text=dates_txt,
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_secondaire"],
                         justify="left").pack(
                             anchor="w", padx=8, pady=(0, 6))

    def _vider_historique(self):
        for w in self.frame_historique.winfo_children():
            w.destroy()

    # ── Actions ───────────────────────────────────────────────────
    def _ouvrir_enreg_conge(self):
        if not self._solde_sel or not self._emp_sel:
            return
        DialogueConge(self,
                      employe_data=self._emp_sel,
                      solde_data=self._solde_sel,
                      callback_succes=self._apres_action)

    def _ouvrir_modif_solde(self):
        if not self._solde_sel or not self._emp_sel:
            return
        DialogueSolde(self,
                      employe_data=self._emp_sel,
                      solde_data=self._solde_sel,
                      callback_succes=self._apres_action)

    def _ouvrir_nouveau_solde(self):
        if not self._emp_sel:
            return
        DialogueSolde(self,
                      employe_data=self._emp_sel,
                      solde_data=None,
                      callback_succes=self._apres_action)

    def _annuler_mouvement(self, mouvement_id: int):
        dlg = DialogueConfirmation(
            self,
            titre="Annuler ce mouvement",
            message="Les jours seront restitués au solde.\n\n"
                    "Confirmer l'annulation ?",
            texte_confirmer="Annuler le congé",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            conges_dao.annuler_mouvement(mouvement_id)
            self._apres_action({})

    def _apres_action(self, resultat: dict):
        self._filtrer()

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
