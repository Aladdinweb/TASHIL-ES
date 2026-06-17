# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Génération et historique des Bordereaux d'envoi — EPSP ES-SENIA
"""
import os
import datetime
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import bordereaux_dao, conges_dao
from app.utils.deduction_engine import obtenir_soldes_ordonnes
from app.reports.bordereau_excel import generer_bordereau
from app.views.dialogue_confirmation import DialogueConfirmation


# ── Catégories disponibles ────────────────────────────────────────
CATEGORIES = [
    ("CONGE_ANNUEL",              "Congé Annuel"),
    ("CERTIFICAT_MEDICAL_ARRET",  "Certificat Médical d'Arrêt"),
    ("CERTIFICAT_MEDICAL_REPRISE","Certificat Médical de Reprise"),
    ("DEMANDE_3_JOURS_NAISSANCE", "Demande 3 Jours Naissance"),
    ("DEMANDE_ANNULATION_CONGE",  "Demande d'Annulation de Congé"),
]


class VueBordereaux(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._lignes_en_cours: list = []
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Bordereaux d'envoi",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, 12))

        # Deux panneaux : gauche=nouveau, droite=historique
        frame_corps = ctk.CTkFrame(self, fg_color="transparent")
        frame_corps.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        frame_corps.grid_columnconfigure(0, weight=3)
        frame_corps.grid_columnconfigure(1, weight=2)
        frame_corps.grid_rowconfigure(0, weight=1)

        self._construire_panneau_creation(frame_corps)
        self._construire_panneau_historique(frame_corps)

    # ── Panneau création ──────────────────────────────────────────
    def _construire_panneau_creation(self, parent):
        frame = ctk.CTkScrollableFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        def sep(texte):
            f = ctk.CTkFrame(frame, fg_color="transparent")
            f.pack(fill="x", padx=14, pady=(14, 4))
            ctk.CTkLabel(f, text=texte, font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                         side="left", fill="x", expand=True, padx=(8, 0))

        def champ(parent_f, label, placeholder="", val_defaut=""):
            f = ctk.CTkFrame(parent_f, fg_color="transparent")
            f.pack(fill="x", padx=14, pady=(0, 10))
            ctk.CTkLabel(f, text=label, font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w")
            e = ctk.CTkEntry(
                f, placeholder_text=placeholder,
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"], height=36,
                corner_radius=DIMENSIONS["rayon_bouton"])
            e.pack(fill="x", pady=(4, 0))
            if val_defaut:
                e.insert(0, val_defaut)
            return e

        sep("En-tête du Bordereau")

        numero_auto = bordereaux_dao.prochain_numero()
        self.e_numero = champ(frame, "Numéro", "Ex : 001/2025",
                              numero_auto)
        self.e_date   = champ(frame, "Date d'émission",
                              "JJ/MM/AAAA",
                              datetime.date.today().strftime("%d/%m/%Y"))
        self.e_exped  = champ(frame, "Expéditeur (service)",
                              "Ex : Service des Soins",
                              "EPSP ES-SENIA")
        self.e_dest   = champ(frame, "Destinataire",
                              "Ex : Direction",
                              "Monsieur le Directeur de l'EPSP ES-SENIA")
        self.e_objet  = champ(frame, "Objet",
                              "Ex : Transmission de documents",
                              "TRANSMISSION DE DOCUMENTS ADMINISTRATIFS")

        sep("Pièces à inclure")

        # Zone ajout de pièce
        frame_ajout = ctk.CTkFrame(frame,
                                   fg_color=COULEURS["bg_sidebar"],
                                   corner_radius=8)
        frame_ajout.pack(fill="x", padx=14, pady=(0, 10))

        f_cat = ctk.CTkFrame(frame_ajout, fg_color="transparent")
        f_cat.pack(fill="x", padx=10, pady=(10, 6))
        ctk.CTkLabel(f_cat, text="Catégorie :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.m_categorie = ctk.CTkOptionMenu(
            f_cat,
            values=[c[1] for c in CATEGORIES],
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._on_categorie_change)
        self.m_categorie.pack(fill="x", pady=(4, 0))

        # Sélecteur employé (pour CONGE_ANNUEL)
        self.frame_emp_select = ctk.CTkFrame(
            frame_ajout, fg_color="transparent")
        self.frame_emp_select.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_emp_select, text="Employé :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")

        employes = conges_dao.lister_employes_actifs()
        self._employes_list = employes
        noms_emp = [f"{e['matricule']} — {e['nom']} {e['prenom']}"
                    for e in employes]
        self.m_employe = ctk.CTkOptionMenu(
            self.frame_emp_select,
            values=noms_emp if noms_emp else ["Aucun employé"],
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._on_employe_change)
        self.m_employe.pack(fill="x", pady=(4, 0))

        # Sélecteur solde/mouvement
        self.frame_solde_select = ctk.CTkFrame(
            frame_ajout, fg_color="transparent")
        self.frame_solde_select.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(self.frame_solde_select, text="Mouvement :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.m_mouvement = ctk.CTkOptionMenu(
            self.frame_solde_select,
            values=["— Sélectionner un employé d'abord —"],
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.m_mouvement.pack(fill="x", pady=(4, 0))
        self._mouvements_cache = []

        # Désignation libre
        f_des = ctk.CTkFrame(frame_ajout, fg_color="transparent")
        f_des.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkLabel(f_des, text="Désignation (ou texte libre) :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.e_designation = ctk.CTkEntry(
            f_des,
            placeholder_text="Saisie automatique ou manuelle",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.e_designation.pack(fill="x", pady=(4, 0))

        ctk.CTkButton(
            frame_ajout, text="＋  Ajouter cette pièce",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ajouter_piece
        ).pack(fill="x", padx=10, pady=(4, 10))

        sep("Récapitulatif des pièces")

        self.frame_recap = ctk.CTkScrollableFrame(
            frame, fg_color=COULEURS["bg_sidebar"],
            corner_radius=6, height=160,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_recap.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_recap_vide = ctk.CTkLabel(
            self.frame_recap,
            text="Aucune pièce ajoutée.",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"])
        self.lbl_recap_vide.pack(pady=14)

        # Bouton générer
        ctk.CTkButton(
            frame, text="📄  Générer le Bordereau Excel",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"], height=40,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._generer
        ).pack(fill="x", padx=14, pady=(0, 14))

    # ── Panneau historique ────────────────────────────────────────
    def _construire_panneau_historique(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COULEURS["bg_carte"],
                             corner_radius=8)
        frame.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(frame, text="Bordereaux générés",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(frame, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        self.frame_historique = ctk.CTkScrollableFrame(
            frame, fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_historique.pack(fill="both", expand=True,
                                   padx=14, pady=(0, 14))
        self._charger_historique()

    def _charger_historique(self):
        for w in self.frame_historique.winfo_children():
            w.destroy()
        bordereaux = bordereaux_dao.lister_bordereaux()
        if not bordereaux:
            ctk.CTkLabel(self.frame_historique,
                         text="Aucun bordereau généré.",
                         font=POLICES["corps"],
                         text_color=COULEURS["texte_discret"]).pack(pady=20)
            return
        for b in bordereaux:
            f = ctk.CTkFrame(self.frame_historique,
                             fg_color=COULEURS["bg_carte"],
                             corner_radius=6)
            f.pack(fill="x", pady=4)
            ctk.CTkLabel(f,
                         text=f"📄  N° {b['numero']}",
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_principal"]).pack(
                             anchor="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(f,
                         text=f"{b['date_emission']}  —  "
                              f"{b['nb_pieces']} pièce(s)",
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w", padx=10)

            f_btns = ctk.CTkFrame(f, fg_color="transparent")
            f_btns.pack(fill="x", padx=10, pady=(4, 8))
            bid = b["id"]
            fich = b.get("chemin_fichier", "")

            if fich and os.path.exists(fich):
                ctk.CTkButton(
                    f_btns, text="📂 Ouvrir",
                    fg_color=COULEURS["accent_vert"],
                    hover_color="#059669",
                    text_color="#FFFFFF",
                    font=POLICES["petit"], height=26,
                    corner_radius=4,
                    command=lambda p=fich: os.startfile(p)
                ).pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                f_btns, text="🗑",
                fg_color="transparent",
                hover_color=COULEURS["accent_rouge"],
                text_color=COULEURS["texte_discret"],
                font=POLICES["petit"], height=26, width=28,
                corner_radius=4,
                command=lambda i=bid: self._supprimer_bordereau(i)
            ).pack(side="left")

    # ── Logique sélection employé/mouvement ──────────────────────
    def _on_categorie_change(self, val):
        pass

    def _on_employe_change(self, val):
        idx = next((i for i, e in enumerate(self._employes_list)
                    if f"{e['matricule']} — {e['nom']} {e['prenom']}" == val),
                   None)
        if idx is None:
            return
        emp = self._employes_list[idx]
        mouvements = conges_dao.lister_mouvements(employe_id=emp["id"])
        self._mouvements_cache = mouvements
        if mouvements:
            labels = []
            for m in mouvements:
                try:
                    d1 = datetime.date.fromisoformat(
                        m["date_debut"]).strftime("%d/%m/%Y")
                    d2 = datetime.date.fromisoformat(
                        m["date_fin"]).strftime("%d/%m/%Y")
                except Exception:
                    d1, d2 = m["date_debut"], m["date_fin"]
                labels.append(
                    f"{m['annee']} | {d1}→{d2} | {m['nb_jours']:.0f}j")
            self.m_mouvement.configure(values=labels)
            self.m_mouvement.set(labels[0])
            self._auto_remplir_designation(emp, mouvements[0])
        else:
            self.m_mouvement.configure(
                values=["Aucun mouvement enregistré"])
            self.m_mouvement.set("Aucun mouvement enregistré")

    def _auto_remplir_designation(self, emp: dict, mouvement: dict):
        """Construit automatiquement la désignation formatée EPSP."""
        try:
            d1 = datetime.date.fromisoformat(
                mouvement["date_debut"]).strftime("%d/%m/%Y")
            d2 = datetime.date.fromisoformat(
                mouvement["date_fin"]).strftime("%d/%m/%Y")
        except Exception:
            d1 = mouvement["date_debut"]
            d2 = mouvement["date_fin"]

        cat_sel = self.m_categorie.get()
        if cat_sel == "Congé Annuel":
            designation = (
                f"{emp['nom']} {emp['prenom']} "
                f"({emp.get('grade', '')}), "
                f"{mouvement['nb_jours']:.0f} jour(s), "
                f"exercice {mouvement['annee']}, "
                f"du {d1} au {d2}"
            )
        else:
            designation = (
                f"{emp['nom']} {emp['prenom']} "
                f"({emp.get('grade', '')}), "
                f"du {d1} au {d2}"
            )

        self.e_designation.delete(0, "end")
        self.e_designation.insert(0, designation)

    def _cat_interne(self, libelle: str) -> str:
        return next((c[0] for c in CATEGORIES if c[1] == libelle),
                    "CONGE_ANNUEL")

    def _ajouter_piece(self):
        designation = self.e_designation.get().strip()
        if not designation:
            messagebox.showwarning("Champ vide",
                                   "La désignation ne peut pas être vide.")
            return
        cat_interne = self._cat_interne(self.m_categorie.get())

        mouvement_id = None
        if self._mouvements_cache:
            idx_m = self.m_mouvement.cget("values").index(
                self.m_mouvement.get()) \
                if self.m_mouvement.get() in \
                   list(self.m_mouvement.cget("values")) else 0
            if idx_m < len(self._mouvements_cache):
                mouvement_id = self._mouvements_cache[idx_m]["id"]

        piece = {
            "categorie":    cat_interne,
            "designation":  designation,
            "nb_pieces":    1,
            "observation":  "Pour toutes fins utiles",
            "mouvement_id": mouvement_id,
        }
        self._lignes_en_cours.append(piece)
        self._rafraichir_recap()
        self.e_designation.delete(0, "end")

    def _rafraichir_recap(self):
        for w in self.frame_recap.winfo_children():
            w.destroy()
        if not self._lignes_en_cours:
            ctk.CTkLabel(self.frame_recap,
                         text="Aucune pièce ajoutée.",
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_discret"]).pack(pady=14)
            return
        for idx, piece in enumerate(self._lignes_en_cours):
            f = ctk.CTkFrame(self.frame_recap,
                             fg_color=COULEURS["bg_carte"],
                             corner_radius=4)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f,
                         text=f"{idx+1}. {piece['designation'][:60]}…"
                              if len(piece['designation']) > 60
                              else f"{idx+1}. {piece['designation']}",
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_principal"],
                         anchor="w", wraplength=320).pack(
                             side="left", padx=8, pady=4)
            ctk.CTkButton(
                f, text="✕",
                fg_color="transparent",
                hover_color=COULEURS["accent_rouge"],
                text_color=COULEURS["texte_discret"],
                font=POLICES["petit"],
                width=22, height=22,
                corner_radius=4,
                command=lambda i=idx: self._supprimer_piece(i)
            ).pack(side="right", padx=4)

    def _supprimer_piece(self, idx: int):
        if 0 <= idx < len(self._lignes_en_cours):
            self._lignes_en_cours.pop(idx)
            self._rafraichir_recap()

    def _generer(self):
        if not self._lignes_en_cours:
            messagebox.showwarning("Aucune pièce",
                                   "Ajoutez au moins une pièce.")
            return
        numero = self.e_numero.get().strip()
        date   = self.e_date.get().strip()
        if not numero or not date:
            messagebox.showwarning("Champs manquants",
                                   "Le numéro et la date sont obligatoires.")
            return

        data_bord = {
            "numero":       numero,
            "date":         date,
            "date_emission":date,
            "expediteur":   self.e_exped.get().strip(),
            "destinataire": self.e_dest.get().strip(),
            "objet":        self.e_objet.get().strip(),
            "lignes":       self._lignes_en_cours,
        }

        try:
            from app.utils.database import faire_backup
            faire_backup('bordereau')
            chemin = generer_bordereau(data_bord)
            data_bord["chemin_fichier"] = chemin
            bordereaux_dao.creer_bordereau(data_bord)
            self._lignes_en_cours = []
            self._rafraichir_recap()
            self._charger_historique()
            messagebox.showinfo(
                "Succès",
                f"Bordereau généré avec succès !\n\n{chemin}")
            if os.path.exists(chemin):
                os.startfile(chemin)
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _supprimer_bordereau(self, bord_id: int):
        dlg = DialogueConfirmation(
            self,
            titre="Supprimer le bordereau",
            message="Supprimer cet enregistrement ?\n"
                    "Le fichier Excel n'est pas supprimé.",
            texte_confirmer="Supprimer",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            bordereaux_dao.supprimer_bordereau(bord_id)
            self._charger_historique()

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
