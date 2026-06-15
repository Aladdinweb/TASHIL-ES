# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion des Employés — EPSP ES-SENIA
CRUD complet avec recherche, filtre département, et actions contextuelles.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import employes_dao
from app.views.dialogue_employe import DialogueEmploye
from app.views.dialogue_confirmation import DialogueConfirmation


class VueEmployes(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._emp_selectionne_id: int = None
        self._depts = []
        self._construire()

    # ── Construction ──────────────────────────────────────────────
    def _construire(self):
        pad = DIMENSIONS["padding_page"]
        self._depts = employes_dao.lister_departements()

        # Titre + bouton ajout
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Gestion des Employés",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        ctk.CTkButton(
            frame_titre, text="＋  Nouvel employé",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=36, corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ouvrir_creation
        ).pack(side="right")

        # Séparateur
        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, pad))

        # Barre filtres
        frame_filtres = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtres.pack(fill="x", padx=pad, pady=(0, 12))

        self.e_recherche = ctk.CTkEntry(
            frame_filtres,
            placeholder_text="🔍  Rechercher par nom, prénom ou matricule…",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"],
            height=36, corner_radius=DIMENSIONS["rayon_bouton"],
            width=340
        )
        self.e_recherche.pack(side="left", padx=(0, 10))
        self.e_recherche.bind("<KeyRelease>", lambda e: self._filtrer())

        noms_depts = (["Tous les départements"] +
                      [f"{d['code']} — {d['nom']}" for d in self._depts])
        self.m_dept = ctk.CTkOptionMenu(
            frame_filtres, values=noms_depts,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            dropdown_font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=240, height=36,
            command=lambda v: self._filtrer()
        )
        self.m_dept.pack(side="left", padx=(0, 10))

        # Compteur
        self.lbl_compteur = ctk.CTkLabel(
            frame_filtres, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        )
        self.lbl_compteur.pack(side="left", padx=(6, 0))

        # Panneau principal : liste + détail
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.pack(fill="both", expand=True,
                             padx=pad, pady=(0, 0))
        frame_principal.grid_columnconfigure(0, weight=3)
        frame_principal.grid_columnconfigure(1, weight=1)
        frame_principal.grid_rowconfigure(0, weight=1)

        # Liste employés
        self._construire_liste(frame_principal)

        # Panneau détail / actions
        self._construire_panneau_detail(frame_principal)

        # Pied de page
        self._construire_pied(pad)

        # Chargement initial
        self._filtrer()

    def _construire_liste(self, parent):
        cols = [
            ("Matricule",    100),
            ("Nom & Prénom", 195),
            ("Grade",        165),
            ("Département",  110),
            ("Radio",         55),
            ("Statut",        70),
        ]
        # En-têtes
        frame_head = ctk.CTkFrame(parent,
                                  fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=8)
        frame_head.grid(row=0, column=0, sticky="new", padx=(0, 8), pady=(0, 2))
        for col_nom, col_larg in cols:
            ctk.CTkLabel(frame_head, text=col_nom,
                         font=POLICES["tableau_head"],
                         text_color=COULEURS["texte_secondaire"],
                         width=col_larg, anchor="w").pack(
                             side="left", padx=8, pady=8)

        # Corps scrollable
        self.frame_liste = ctk.CTkScrollableFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"]
        )
        self.frame_liste.grid(row=0, column=0, sticky="nsew",
                              padx=(0, 8), pady=(42, pad))
        self._cols = cols

    def _construire_panneau_detail(self, parent):
        self.frame_detail = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8
        )
        self.frame_detail.grid(row=0, column=1, sticky="nsew",
                               pady=(0, DIMENSIONS["padding_page"]))

        ctk.CTkLabel(self.frame_detail,
                     text="Détail / Actions",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         padx=16, pady=(16, 4), anchor="w")
        ctk.CTkFrame(self.frame_detail, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=16, pady=(0, 12))

        self.lbl_detail_nom = ctk.CTkLabel(
            self.frame_detail, text="Aucun employé\nsélectionné",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"],
            justify="center", wraplength=160)
        self.lbl_detail_nom.pack(pady=(20, 4))

        self.lbl_detail_info = ctk.CTkLabel(
            self.frame_detail, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"],
            justify="center", wraplength=160)
        self.lbl_detail_info.pack(pady=(0, 20))

        ctk.CTkFrame(self.frame_detail, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=16, pady=(0, 16))

        # Boutons actions
        self.btn_modifier = ctk.CTkButton(
            self.frame_detail, text="✏  Modifier",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=34, corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._ouvrir_modification
        )
        self.btn_modifier.pack(fill="x", padx=16, pady=(0, 8))

        self.btn_supprimer = ctk.CTkButton(
            self.frame_detail, text="🗑  Désactiver",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"],
            height=34, corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._confirmer_suppression
        )
        self.btn_supprimer.pack(fill="x", padx=16, pady=(0, 8))

        self.btn_restaurer = ctk.CTkButton(
            self.frame_detail, text="♻  Restaurer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_vert"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"],
            height=34, corner_radius=DIMENSIONS["rayon_bouton"],
            state="disabled",
            command=self._confirmer_restauration
        )
        self.btn_restaurer.pack(fill="x", padx=16, pady=(0, 8))

    def _construire_pied(self, pad):
        frame_pied = ctk.CTkFrame(self, fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=0, height=44)
        frame_pied.pack(fill="x", side="bottom")
        frame_pied.pack_propagate(False)
        self.lbl_pied = ctk.CTkLabel(
            frame_pied, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_pied.pack(side="left", padx=pad, pady=0)

    # ── Filtrage & affichage ───────────────────────────────────────
    def _filtrer(self):
        recherche = self.e_recherche.get().strip()
        dept_sel  = self.m_dept.get()

        dept_id = None
        if dept_sel and dept_sel != "Tous les départements":
            code = dept_sel.split("—")[0].strip()
            for d in self._depts:
                if d["code"] == code:
                    dept_id = d["id"]
                    break

        employes = employes_dao.lister_employes(
            dept_id=dept_id, recherche=recherche)
        self._afficher_employes(employes)
        self.lbl_compteur.configure(
            text=f"{len(employes)} employé(s)")

    def _afficher_employes(self, employes: list):
        # Vider la liste
        for w in self.frame_liste.winfo_children():
            w.destroy()
        self._emp_selectionne_id = None
        self._reinitialiser_detail()

        if not employes:
            ctk.CTkLabel(
                self.frame_liste,
                text="Aucun employé trouvé.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        for idx, emp in enumerate(employes):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0 else COULEURS["bg_champ"])
            frame_ligne = ctk.CTkFrame(
                self.frame_liste, fg_color=bg,
                corner_radius=0, cursor="hand2")
            frame_ligne.pack(fill="x", pady=1)

            valeurs = [
                emp["matricule"],
                f"{emp['nom']} {emp['prenom']}",
                emp["grade"],
                emp["dept_code"],
                "✓" if emp["est_manip_radio"] else "—",
                "Actif" if emp["actif"] else "Inactif",
            ]

            for i, (_, col_larg) in enumerate(self._cols):
                val = valeurs[i] if i < len(valeurs) else ""
                couleur_txt = COULEURS["texte_principal"]
                if i == 5:  # Colonne statut
                    couleur_txt = (COULEURS["accent_vert"]
                                   if emp["actif"]
                                   else COULEURS["accent_rouge"])
                ctk.CTkLabel(
                    frame_ligne, text=str(val),
                    font=POLICES["tableau"],
                    text_color=couleur_txt,
                    width=col_larg, anchor="w"
                ).pack(side="left", padx=8, pady=6)

            emp_id = emp["id"]

            def on_enter(e, f=frame_ligne):
                f.configure(fg_color=COULEURS["bg_hover"])
            def on_leave(e, f=frame_ligne, b=bg):
                f.configure(fg_color=b)
            def on_click(e, eid=emp_id, emp_data=emp):
                self._selectionner_employe(eid, emp_data)

            frame_ligne.bind("<Enter>", on_enter)
            frame_ligne.bind("<Leave>", on_leave)
            frame_ligne.bind("<Button-1>", on_click)
            for child in frame_ligne.winfo_children():
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
                child.bind("<Button-1>", on_click)

    # ── Sélection ─────────────────────────────────────────────────
    def _selectionner_employe(self, emp_id: int, emp: dict):
        self._emp_selectionne_id = emp_id
        nom_complet = f"{emp['nom']}\n{emp['prenom']}"
        info = (f"{emp['grade']}\n{emp['dept_code']}\n"
                f"{'⚡ Protection radiation' if emp['est_manip_radio'] else ''}")

        self.lbl_detail_nom.configure(text=nom_complet,
                                      text_color=COULEURS["texte_principal"])
        self.lbl_detail_info.configure(text=info.strip())

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
        self.lbl_detail_nom.configure(
            text="Aucun employé\nsélectionné",
            text_color=COULEURS["texte_secondaire"])
        self.lbl_detail_info.configure(text="")
        self.btn_modifier.configure(state="disabled")
        self.btn_supprimer.configure(state="disabled")
        self.btn_restaurer.configure(state="disabled")
        self.lbl_pied.configure(text="")

    # ── Actions CRUD ──────────────────────────────────────────────
    def _ouvrir_creation(self):
        DialogueEmploye(self, callback_succes=self._apres_sauvegarde)

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
            message="Cet employé sera marqué comme inactif.\n"
                    "Ses données et congés sont conservés.\n\n"
                    "Confirmer la désactivation ?",
            texte_confirmer="Désactiver",
            style="danger"
        )
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.supprimer_employe(self._emp_selectionne_id)
            self._apres_sauvegarde({"action": "desactive"})

    def _confirmer_restauration(self):
        if not self._emp_selectionne_id:
            return
        dlg = DialogueConfirmation(
            self,
            titre="Restaurer l'employé",
            message="Cet employé sera remis en statut actif.\n\n"
                    "Confirmer la restauration ?",
            texte_confirmer="Restaurer",
            style="succes"
        )
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.restaurer_employe(self._emp_selectionne_id)
            self._apres_sauvegarde({"action": "restaure"})

    def _apres_sauvegarde(self, resultat: dict):
        self._filtrer()

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
