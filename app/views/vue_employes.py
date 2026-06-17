# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion des Employés — EPSP ES-SENIA
CRUD complet avec recherche, filtre, polyclinique, et état vide clair.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import employes_dao
from app.utils.polycliniques_dao import lister_polycliniques
from app.views.dialogue_employe import DialogueEmploye
from app.views.dialogue_confirmation import DialogueConfirmation


class VueEmployes(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._emp_selectionne_id = None
        self._depts = []
        self._polys = []
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]
        self._depts = employes_dao.lister_departements()
        self._polys = lister_polycliniques()

        # ── Titre + bouton ajout ──────────────────────────────
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))

        ctk.CTkLabel(frame_titre, text="Gestion des Employés",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")

        ctk.CTkButton(
            frame_titre,
            text="＋  Nouvel employé",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=40,
            width=180,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ouvrir_creation
        ).pack(side="right")

        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, 12))

        # ── Filtres ───────────────────────────────────────────
        frame_f = ctk.CTkFrame(self, fg_color="transparent")
        frame_f.pack(fill="x", padx=pad, pady=(0, 10))

        self.e_recherche = ctk.CTkEntry(
            frame_f,
            placeholder_text="🔍  Rechercher par nom ou matricule…",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=36,
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=280)
        self.e_recherche.pack(side="left", padx=(0, 8))
        self.e_recherche.bind("<KeyRelease>",
                              lambda e: self._filtrer())

        noms_depts = (["Tous les départements"] +
                      [f"{d['code']} — {d['nom']}"
                       for d in self._depts])
        self.m_dept = ctk.CTkOptionMenu(
            frame_f, values=noms_depts,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=210, height=36,
            command=lambda v: self._filtrer())
        self.m_dept.pack(side="left", padx=(0, 8))

        noms_polys = (["Toutes les polycliniques"] +
                      [p["nom"] for p in self._polys])
        self.m_poly = ctk.CTkOptionMenu(
            frame_f, values=noms_polys,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=240, height=36,
            command=lambda v: self._filtrer())
        self.m_poly.pack(side="left", padx=(0, 8))

        self.lbl_compteur = ctk.CTkLabel(
            frame_f, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_compteur.pack(side="left")

        # ── Corps : liste + détail ────────────────────────────
        frame_corps = ctk.CTkFrame(self, fg_color="transparent")
        frame_corps.pack(fill="both", expand=True,
                         padx=pad, pady=(0, 0))
        frame_corps.grid_columnconfigure(0, weight=3)
        frame_corps.grid_columnconfigure(1, weight=1)
        frame_corps.grid_rowconfigure(0, weight=1)

        self._construire_liste(frame_corps)
        self._construire_detail(frame_corps)

        # Pied
        frame_pied = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=44)
        frame_pied.pack(fill="x", side="bottom")
        frame_pied.pack_propagate(False)
        self.lbl_pied = ctk.CTkLabel(
            frame_pied, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_pied.pack(side="left", padx=pad)

        self._filtrer()

    def _construire_liste(self, parent):
        self._cols = [
            ("Matricule",    100),
            ("Nom & Prénom", 180),
            ("Grade",        155),
            ("Dép.",          60),
            ("Polyclinique", 160),
            ("Radio",         50),
            ("Statut",        65),
        ]
        frame_head = ctk.CTkFrame(
            parent, fg_color=COULEURS["bg_sidebar"],
            corner_radius=8)
        frame_head.grid(row=0, column=0, sticky="new",
                        padx=(0, 8), pady=(0, 2))
        for nom, larg in self._cols:
            ctk.CTkLabel(
                frame_head, text=nom,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=larg, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        self.frame_liste = ctk.CTkScrollableFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_liste.grid(
            row=0, column=0, sticky="nsew",
            padx=(0, 8),
            pady=(40, DIMENSIONS["padding_page"]))

    def _construire_detail(self, parent):
        self.frame_detail = ctk.CTkFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        self.frame_detail.grid(
            row=0, column=1, sticky="nsew",
            pady=(0, DIMENSIONS["padding_page"]))

        ctk.CTkLabel(self.frame_detail,
                     text="Actions",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(self.frame_detail, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        # Bouton ajout bien visible dans le panneau aussi
        ctk.CTkButton(
            self.frame_detail,
            text="＋  Nouvel employé",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=36,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ouvrir_creation
        ).pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkFrame(self.frame_detail, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        self.lbl_sel_nom = ctk.CTkLabel(
            self.frame_detail,
            text="Cliquez sur un\nemployé pour\nle sélectionner",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"],
            justify="center", wraplength=160)
        self.lbl_sel_nom.pack(pady=(10, 2))

        self.lbl_sel_info = ctk.CTkLabel(
            self.frame_detail, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"],
            justify="center", wraplength=160)
        self.lbl_sel_info.pack(pady=(0, 16))

        ctk.CTkFrame(self.frame_detail, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        self.btn_modifier = ctk.CTkButton(
            self.frame_detail, text="✏  Modifier",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._ouvrir_modification)
        self.btn_modifier.pack(fill="x", padx=14, pady=(0, 8))

        self.btn_supprimer = ctk.CTkButton(
            self.frame_detail, text="🗑  Désactiver",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._confirmer_suppression)
        self.btn_supprimer.pack(fill="x", padx=14, pady=(0, 8))

        self.btn_restaurer = ctk.CTkButton(
            self.frame_detail, text="♻  Restaurer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_vert"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._confirmer_restauration)
        self.btn_restaurer.pack(fill="x", padx=14, pady=(0, 8))

    # ── Filtrage ──────────────────────────────────────────────
    def _filtrer(self):
        recherche = self.e_recherche.get().strip()
        dept_sel  = self.m_dept.get()
        poly_sel  = self.m_poly.get()

        dept_id = None
        if dept_sel and dept_sel != "Tous les départements":
            code = dept_sel.split("—")[0].strip()
            for d in self._depts:
                if d["code"] == code:
                    dept_id = d["id"]
                    break

        employes = employes_dao.lister_employes(
            dept_id=dept_id, recherche=recherche)

        # Filtre polyclinique côté Python
        if poly_sel and poly_sel != "Toutes les polycliniques":
            poly_id = next(
                (p["id"] for p in self._polys
                 if p["nom"] == poly_sel), None)
            if poly_id:
                employes = [e for e in employes
                            if e.get("polyclinique_id") == poly_id]

        self._afficher_employes(employes)
        self.lbl_compteur.configure(
            text=f"{len(employes)} employé(s)")

    def _afficher_employes(self, employes: list):
        for w in self.frame_liste.winfo_children():
            w.destroy()
        self._emp_selectionne_id = None
        self._reinitialiser_detail()

        if not employes:
            # État vide clair avec invitation à agir
            frame_vide = ctk.CTkFrame(
                self.frame_liste, fg_color="transparent")
            frame_vide.pack(expand=True, pady=60)

            ctk.CTkLabel(
                frame_vide, text="👤",
                font=("Segoe UI", 48),
                text_color=COULEURS["texte_discret"]).pack()
            ctk.CTkLabel(
                frame_vide,
                text="Aucun employé dans la base de données.",
                font=POLICES["sous_titre"],
                text_color=COULEURS["texte_secondaire"]).pack(
                    pady=(8, 4))
            ctk.CTkLabel(
                frame_vide,
                text="Cliquez sur « ＋ Nouvel employé » pour commencer.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]).pack()

            ctk.CTkButton(
                frame_vide,
                text="＋  Ajouter le premier employé",
                fg_color=COULEURS["accent_vert"],
                hover_color="#059669",
                text_color="#FFFFFF",
                font=POLICES["bouton"],
                height=42, width=280,
                corner_radius=DIMENSIONS["rayon_bouton"],
                command=self._ouvrir_creation
            ).pack(pady=(20, 0))
            return

        for idx, emp in enumerate(employes):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0 else COULEURS["bg_champ"])
            frame_l = ctk.CTkFrame(
                self.frame_liste, fg_color=bg,
                corner_radius=0, cursor="hand2")
            frame_l.pack(fill="x", pady=1)

            # Nom polyclinique (abrégé)
            poly_nom = emp.get("poly_nom", "") or ""
            poly_court = (poly_nom.replace("POLYCLINIQUE ", "")[:15]
                          if poly_nom else "—")

            valeurs = [
                emp["matricule"],
                f"{emp['nom']} {emp['prenom']}",
                emp["grade"][:18] if emp["grade"] else "",
                emp.get("dept_code", ""),
                poly_court,
                "✓" if emp["est_manip_radio"] else "—",
                "Actif" if emp["actif"] else "Inactif",
            ]

            for i, (_, larg) in enumerate(self._cols):
                coul = COULEURS["texte_principal"]
                if i == 6:
                    coul = (COULEURS["accent_vert"]
                            if emp["actif"]
                            else COULEURS["accent_rouge"])
                ctk.CTkLabel(
                    frame_l, text=str(valeurs[i]),
                    font=POLICES["tableau"],
                    text_color=coul,
                    width=larg, anchor="w"
                ).pack(side="left", padx=6, pady=6)

            eid  = emp["id"]
            edat = emp

            def on_enter(e, f=frame_l):
                f.configure(fg_color=COULEURS["bg_hover"])
            def on_leave(e, f=frame_l, b=bg):
                f.configure(fg_color=b)
            def on_click(e, i=eid, d=edat):
                self._selectionner(i, d)

            for w in [frame_l] + frame_l.winfo_children():
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", on_click)

    def _selectionner(self, emp_id, emp):
        self._emp_selectionne_id = emp_id
        poly_txt = emp.get("poly_nom") or "—"
        if len(poly_txt) > 25:
            poly_txt = poly_txt[:22] + "…"
        self.lbl_sel_nom.configure(
            text=f"{emp['nom']}\n{emp['prenom']}",
            text_color=COULEURS["texte_principal"])
        self.lbl_sel_info.configure(
            text=(f"{emp['grade']}\n"
                  f"{emp.get('dept_code','')}\n"
                  f"{poly_txt}\n"
                  f"{'⚡ Radiation' if emp['est_manip_radio'] else ''}").strip())
        self.btn_modifier.configure(state="normal")
        if emp["actif"]:
            self.btn_supprimer.configure(state="normal")
            self.btn_restaurer.configure(state="disabled")
        else:
            self.btn_supprimer.configure(state="disabled")
            self.btn_restaurer.configure(state="normal")
        self.lbl_pied.configure(
            text=f"Sélectionné : {emp['matricule']} — "
                 f"{emp['nom']} {emp['prenom']}")

    def _reinitialiser_detail(self):
        self.lbl_sel_nom.configure(
            text="Cliquez sur un\nemployé pour\nle sélectionner",
            text_color=COULEURS["texte_secondaire"])
        self.lbl_sel_info.configure(text="")
        self.btn_modifier.configure(state="disabled")
        self.btn_supprimer.configure(state="disabled")
        self.btn_restaurer.configure(state="disabled")
        self.lbl_pied.configure(text="")

    def _ouvrir_creation(self):
        DialogueEmploye(self,
                        callback_succes=self._apres_sauvegarde)

    def _ouvrir_modification(self):
        if not self._emp_selectionne_id:
            return
        DialogueEmploye(self,
                        emp_id=self._emp_selectionne_id,
                        callback_succes=self._apres_sauvegarde)

    def _confirmer_suppression(self):
        if not self._emp_selectionne_id:
            return
        dlg = DialogueConfirmation(
            self,
            titre="Désactiver l'employé",
            message="Cet employé sera marqué inactif.\n"
                    "Ses données et congés sont conservés.",
            texte_confirmer="Désactiver",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.supprimer_employe(
                self._emp_selectionne_id)
            self._apres_sauvegarde({})

    def _confirmer_restauration(self):
        if not self._emp_selectionne_id:
            return
        dlg = DialogueConfirmation(
            self,
            titre="Restaurer l'employé",
            message="Cet employé sera remis actif.",
            texte_confirmer="Restaurer",
            style="succes")
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.restaurer_employe(
                self._emp_selectionne_id)
            self._apres_sauvegarde({})

    def _apres_sauvegarde(self, _):
        self._filtrer()

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
