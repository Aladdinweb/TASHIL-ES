# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue Employés — sans bouton doublon, validation assouplie.
Champs obligatoires : Nom, Prénom, Grade, Polyclinique.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import employes_dao
from app.utils.polycliniques_dao import lister_polycliniques
from app.views.dialogue_employe import DialogueEmploye
from app.views.dialogue_confirmation import (
    DialogueConfirmation)


class VueEmployes(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._emp_sel_id = None
        self._depts = []
        self._polys = []
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]
        self._depts = employes_dao.lister_departements()
        self._polys = lister_polycliniques()

        # Titre SANS bouton doublon à droite
        frame_titre = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_titre.pack(
            fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(
            frame_titre,
            text="Gestion des Employés",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        # PAS de bouton "+ Nouvel employé" ici

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 10))

        # Filtres
        frame_f = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_f.pack(
            fill="x", padx=pad, pady=(0, 8))

        self.e_recherche = ctk.CTkEntry(
            frame_f,
            placeholder_text=(
                "🔍  Rechercher nom / matricule…"),
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=280)
        self.e_recherche.pack(
            side="left", padx=(0, 8))
        self.e_recherche.bind(
            "<KeyRelease>",
            lambda e: self._filtrer())

        self.lbl_cpt = ctk.CTkLabel(
            frame_f, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_cpt.pack(side="left")

        # Bouton ajout (position naturelle dans filtres)
        ctk.CTkButton(
            frame_f,
            text="＋  Ajouter",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=34, width=120,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ouvrir_creation
        ).pack(side="right")

        # Layout : liste large, détail étroit
        frame_corps = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_corps.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, 0))
        frame_corps.grid_columnconfigure(0, weight=4)
        frame_corps.grid_columnconfigure(1, weight=1)
        frame_corps.grid_rowconfigure(0, weight=1)

        self._construire_liste(frame_corps)
        self._construire_detail(frame_corps)

        # Pied
        fp = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=40)
        fp.pack(fill="x", side="bottom")
        fp.pack_propagate(False)
        self.lbl_pied = ctk.CTkLabel(
            fp, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_pied.pack(
            side="left", padx=pad)

        self._filtrer()

    def _construire_liste(self, parent):
        self._cols = [
            ("Matricule",    95),
            ("Nom & Prénom", 185),
            ("Grade",        165),
            ("Service",      130),
            ("Polyclinique", 140),
            ("Statut",        65),
        ]
        fh = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=6)
        fh.grid(row=0, column=0,
                sticky="new", padx=(0, 8),
                pady=(0, 2))
        for nom, larg in self._cols:
            ctk.CTkLabel(
                fh, text=nom,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=larg, anchor="w"
            ).pack(side="left", padx=6, pady=7)

        self.frame_liste = ctk.CTkScrollableFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_liste.grid(
            row=0, column=0, sticky="nsew",
            padx=(0, 8),
            pady=(38, DIMENSIONS["padding_page"]))

    def _construire_detail(self, parent):
        self.frame_detail = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        self.frame_detail.grid(
            row=0, column=1, sticky="nsew",
            pady=(0, DIMENSIONS["padding_page"]))

        ctk.CTkLabel(
            self.frame_detail,
            text="Actions",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=14, pady=(14, 4), anchor="w")

        ctk.CTkFrame(
            self.frame_detail, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_sel = ctk.CTkLabel(
            self.frame_detail,
            text="Cliquez sur\nun employé",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"],
            justify="center", wraplength=160)
        self.lbl_sel.pack(pady=(10, 4))

        self.lbl_sel_inf = ctk.CTkLabel(
            self.frame_detail, text="",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"],
            justify="center", wraplength=160)
        self.lbl_sel_inf.pack(pady=(0, 12))

        ctk.CTkFrame(
            self.frame_detail, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=14, pady=(0, 10))

        def btn_act(texte, fg, hov, cmd,
                    txt="#FFFFFF"):
            b = ctk.CTkButton(
                self.frame_detail,
                text=texte,
                fg_color=fg, hover_color=hov,
                text_color=txt,
                font=POLICES["bouton"],
                height=34, state="disabled",
                corner_radius=DIMENSIONS["rayon_bouton"],
                command=cmd)
            b.pack(fill="x", padx=14, pady=(0, 8))
            return b

        self.btn_modif = btn_act(
            "✏  Modifier",
            COULEURS["accent_bleu"],
            COULEURS["accent_bleu_clair"],
            self._ouvrir_modif)

        self.btn_arch = btn_act(
            "📁  Fiche historique",
            COULEURS["bg_champ"],
            COULEURS["bg_hover"],
            self._ouvrir_fiche,
            txt=COULEURS["texte_principal"])

        self.btn_desact = btn_act(
            "🗑  Désactiver",
            COULEURS["bg_champ"],
            COULEURS["accent_rouge"],
            self._confirmer_desact,
            txt=COULEURS["texte_secondaire"])

        self.btn_rest = btn_act(
            "♻  Restaurer",
            COULEURS["bg_champ"],
            COULEURS["accent_vert"],
            self._confirmer_rest,
            txt=COULEURS["texte_secondaire"])

    def _filtrer(self):
        r  = self.e_recherche.get().strip()
        emps = employes_dao.lister_employes(
            recherche=r)
        self._afficher(emps)
        self.lbl_cpt.configure(
            text=f"{len(emps)} employé(s)")

    def _afficher(self, emps):
        for w in self.frame_liste.winfo_children():
            w.destroy()
        self._emp_sel_id = None
        self._reinit_detail()

        if not emps:
            f = ctk.CTkFrame(
                self.frame_liste,
                fg_color="transparent")
            f.pack(expand=True, pady=50)
            ctk.CTkLabel(
                f, text="👤",
                font=("Segoe UI", 48),
                text_color=COULEURS["texte_discret"]
            ).pack()
            ctk.CTkLabel(
                f, text="Aucun employé.",
                font=POLICES["sous_titre"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(pady=8)
            ctk.CTkButton(
                f, text="＋  Ajouter le premier",
                fg_color=COULEURS["accent_vert"],
                hover_color="#059669",
                text_color="#FFFFFF",
                font=POLICES["bouton"],
                height=38, width=240,
                corner_radius=DIMENSIONS["rayon_bouton"],
                command=self._ouvrir_creation
            ).pack()
            return

        for idx, emp in enumerate(emps):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.frame_liste, fg_color=bg,
                corner_radius=0, cursor="hand2")
            fl.pack(fill="x", pady=1)

            poly = (emp.get("poly_nom") or "—")
            if len(poly) > 14:
                poly = poly[:12] + "…"
            svc  = emp.get("dept_code") or "—"
            vals = [
                emp["matricule"],
                f"{emp['nom']} {emp['prenom']}",
                (emp["grade"][:16] + "…"
                 if len(emp["grade"]) > 16
                 else emp["grade"]),
                svc,
                poly,
                "Actif" if emp["actif"]
                else "Inactif",
            ]
            for i, (_, larg) in enumerate(self._cols):
                coul = COULEURS["texte_principal"]
                if i == 5:
                    coul = (COULEURS["accent_vert"]
                            if emp["actif"]
                            else COULEURS["accent_rouge"])
                ctk.CTkLabel(
                    fl, text=vals[i],
                    font=POLICES["tableau"],
                    text_color=coul,
                    width=larg, anchor="w"
                ).pack(side="left", padx=6, pady=5)

            eid = emp["id"]
            edat = emp

            def _enter(e, f=fl):
                f.configure(
                    fg_color=COULEURS["bg_hover"])
            def _leave(e, f=fl, b=bg):
                f.configure(fg_color=b)
            def _click(e, i=eid, d=edat):
                self._selectionner(i, d)
            def _dbl(e, i=eid):
                self._ouvrir_fiche_id(i)

            for w in [fl] + fl.winfo_children():
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)
                w.bind("<Button-1>", _click)
                w.bind("<Double-Button-1>", _dbl)

    def _selectionner(self, eid, emp):
        self._emp_sel_id = eid
        self.lbl_sel.configure(
            text=f"{emp['nom']}\n{emp['prenom']}",
            text_color=COULEURS["texte_principal"])
        self.lbl_sel_inf.configure(
            text=emp.get("grade", ""))
        self.btn_modif.configure(state="normal")
        self.btn_arch.configure(state="normal")
        if emp["actif"]:
            self.btn_desact.configure(state="normal")
            self.btn_rest.configure(state="disabled")
        else:
            self.btn_desact.configure(state="disabled")
            self.btn_rest.configure(state="normal")
        self.lbl_pied.configure(
            text=f"{emp['matricule']} — "
                 f"{emp['nom']} {emp['prenom']}")

    def _reinit_detail(self):
        self.lbl_sel.configure(
            text="Cliquez sur\nun employé",
            text_color=COULEURS["texte_secondaire"])
        self.lbl_sel_inf.configure(text="")
        for b in [self.btn_modif, self.btn_arch,
                  self.btn_desact, self.btn_rest]:
            b.configure(state="disabled")
        self.lbl_pied.configure(text="")

    def _ouvrir_creation(self):
        # Pas de refresh automatique destructif
        def _apres(res):
            # Refresh différé — ne touche pas
            # aux fenêtres ouvertes
            self.after(100, self._filtrer)

        DialogueEmploye(
            self, callback_succes=_apres)

    def _ouvrir_modif(self):
        if not self._emp_sel_id:
            return
        def _apres(res):
            self.after(100, self._filtrer)
        DialogueEmploye(
            self,
            emp_id=self._emp_sel_id,
            callback_succes=_apres)

    def _ouvrir_fiche(self):
        if self._emp_sel_id:
            self._ouvrir_fiche_id(self._emp_sel_id)

    def _ouvrir_fiche_id(self, eid):
        from app.views.fiche_employe import (
            FicheEmploye)
        FicheEmploye(self, emp_id=eid)

    def _confirmer_desact(self):
        if not self._emp_sel_id:
            return
        dlg = DialogueConfirmation(
            self,
            titre="Désactiver",
            message="Désactiver cet employé ?\n"
                    "Données conservées.",
            texte_confirmer="Désactiver",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.supprimer_employe(
                self._emp_sel_id)
            self.after(100, self._filtrer)

    def _confirmer_rest(self):
        if not self._emp_sel_id:
            return
        dlg = DialogueConfirmation(
            self,
            titre="Restaurer",
            message="Remettre cet employé actif ?",
            texte_confirmer="Restaurer",
            style="succes")
        self.wait_window(dlg)
        if dlg.reponse:
            employes_dao.restaurer_employe(
                self._emp_sel_id)
            self.after(100, self._filtrer)

    def rafraichir(self):
        # Refresh prudent : ne détruit PAS
        # les Toplevel actifs
        try:
            self._filtrer()
        except Exception:
            pass
