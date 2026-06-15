# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Gestion du Rollover 1er Mai & Polycliniques — EPSP ES-SENIA
"""
import customtkinter as ctk
import datetime
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.deduction_engine import (
    executer_rollover_mai, verifier_rollover_necessaire)
from app.utils import polycliniques_dao
from app.views.dialogue_confirmation import DialogueConfirmation


class VueRollover(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Administration & Rollover",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, pad))

        # Défilement global
        scroll = ctk.CTkScrollableFrame(self,
                                         fg_color="transparent",
                                         corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self._section_rollover(scroll, pad)
        self._section_polycliniques(scroll, pad)

    # ── Section Rollover ──────────────────────────────────────────
    def _section_rollover(self, parent, pad):
        ctk.CTkLabel(parent, text="Rollover du 1er Mai",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         anchor="w", pady=(0, 8))

        frame_r = ctk.CTkFrame(parent, fg_color=COULEURS["bg_carte"],
                                corner_radius=8)
        frame_r.pack(fill="x", pady=(0, 24))

        # Statut
        necessaire = verifier_rollover_necessaire()
        annee_cloture = datetime.date.today().year - 1

        statut_txt = (
            f"⚠  Rollover {annee_cloture} en attente d'exécution."
            if necessaire else
            f"✓  Rollover {annee_cloture} déjà effectué."
        )
        coul_statut = (COULEURS["accent_orange"] if necessaire
                       else COULEURS["accent_vert"])

        ctk.CTkLabel(frame_r, text=statut_txt,
                     font=POLICES["corps_bold"],
                     text_color=coul_statut).pack(
                         padx=16, pady=(14, 4), anchor="w")

        desc = (
            "Le rollover clôture l'exercice annuel et transfère les\n"
            "jours non consommés en reliquats prioritaires.\n"
            "Un nouveau solde de 30 jours est créé pour chaque employé actif."
        )
        ctk.CTkLabel(frame_r, text=desc, font=POLICES["corps"],
                     text_color=COULEURS["texte_secondaire"],
                     justify="left").pack(padx=16, pady=(0, 10), anchor="w")

        # Sélecteur année
        f_annee = ctk.CTkFrame(frame_r, fg_color="transparent")
        f_annee.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(f_annee, text="Année à clôturer :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         side="left", padx=(0, 10))
        annees = [str(y) for y in range(
            datetime.date.today().year,
            datetime.date.today().year - 5, -1)]
        self.m_annee_rollover = ctk.CTkOptionMenu(
            f_annee, values=annees,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=34, width=120,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.m_annee_rollover.pack(side="left")
        self.m_annee_rollover.set(str(annee_cloture))

        # Boutons
        f_btns = ctk.CTkFrame(frame_r, fg_color="transparent")
        f_btns.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            f_btns, text="👁  Simuler (dry run)",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._simuler_rollover
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_btns, text="⚡  Exécuter le rollover",
            fg_color=COULEURS["accent_orange"],
            hover_color="#D97706",
            text_color="#FFFFFF",
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._executer_rollover
        ).pack(side="left")

        # Zone résultat
        self.frame_res_rollover = ctk.CTkFrame(
            frame_r, fg_color=COULEURS["bg_sidebar"],
            corner_radius=6)
        self.frame_res_rollover.pack(
            fill="x", padx=16, pady=(0, 14))
        self.lbl_res_rollover = ctk.CTkLabel(
            self.frame_res_rollover,
            text="Résultats de la simulation ici.",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"],
            justify="left", wraplength=500)
        self.lbl_res_rollover.pack(padx=10, pady=8, anchor="w")

    def _simuler_rollover(self):
        annee = int(self.m_annee_rollover.get())
        rapport = executer_rollover_mai(annee, dry_run=True)
        txt = (f"SIMULATION — Année {annee}\n"
               f"Employés concernés : {rapport['nb_employes']}\n"
               f"Aucune modification effectuée.")
        self.lbl_res_rollover.configure(
            text=txt, text_color=COULEURS["accent_bleu"])

    def _executer_rollover(self):
        annee = int(self.m_annee_rollover.get())
        dlg = DialogueConfirmation(
            self,
            titre="Confirmer le Rollover",
            message=f"Clôturer l'exercice {annee} pour tous les employés actifs ?\n\n"
                    "Les jours restants deviennent des reliquats prioritaires.\n"
                    "Cette action ne peut pas être annulée.",
            texte_confirmer="Exécuter",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            rapport = executer_rollover_mai(annee, dry_run=False)
            if rapport["statut"] == "deja_fait":
                txt = f"⚠  {rapport['message']}"
                coul = COULEURS["accent_orange"]
            else:
                txt = (f"✓  Rollover {annee} exécuté avec succès.\n"
                       f"Employés traités : {rapport['nb_employes']}\n"
                       f"Nouveaux soldes créés pour {annee + 1}.")
                coul = COULEURS["accent_vert"]
            self.lbl_res_rollover.configure(text=txt, text_color=coul)

    # ── Section Polycliniques ─────────────────────────────────────
    def _section_polycliniques(self, parent, pad):
        ctk.CTkLabel(parent, text="Gestion des Polycliniques",
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         anchor="w", pady=(0, 8))

        polys = polycliniques_dao.lister_polycliniques()
        for poly in polys:
            frame_p = ctk.CTkFrame(parent,
                                   fg_color=COULEURS["bg_carte"],
                                   corner_radius=8)
            frame_p.pack(fill="x", pady=(0, 8))

            f_top = ctk.CTkFrame(frame_p, fg_color="transparent")
            f_top.pack(fill="x", padx=14, pady=(10, 4))
            ctk.CTkLabel(f_top, text=f"🏥  {poly['nom']}",
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_principal"]).pack(
                             side="left")

            # Nombre d'employés
            employes = polycliniques_dao.lister_employes_polyclinique(
                poly["id"])
            ctk.CTkLabel(f_top,
                         text=f"{len(employes)} employé(s)",
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             side="right")

            # Bouton désactiver masse
            f_btns = ctk.CTkFrame(frame_p, fg_color="transparent")
            f_btns.pack(fill="x", padx=14, pady=(0, 10))

            pid = poly["id"]
            ctk.CTkButton(
                f_btns,
                text="🗑  Désactiver tous les employés",
                fg_color="transparent",
                hover_color=COULEURS["accent_rouge"],
                text_color=COULEURS["texte_secondaire"],
                font=POLICES["petit"], height=28,
                corner_radius=4,
                command=lambda p=pid, n=poly["nom"]:
                    self._desactiver_masse(p, n)
            ).pack(side="left")

        if not polys:
            ctk.CTkLabel(parent,
                         text="Aucune polyclinique configurée.",
                         font=POLICES["corps"],
                         text_color=COULEURS["texte_discret"]).pack(pady=20)

    def _desactiver_masse(self, poly_id: int, poly_nom: str):
        dlg = DialogueConfirmation(
            self,
            titre="Désactivation en masse",
            message=f"Désactiver TOUS les employés actifs de :\n\n"
                    f"« {poly_nom} »\n\n"
                    "Les congés et données sont conservés.",
            texte_confirmer="Désactiver tous",
            style="danger")
        self.wait_window(dlg)
        if dlg.reponse:
            count = polycliniques_dao.supprimer_employes_polyclinique(
                poly_id)
            from tkinter import messagebox
            messagebox.showinfo(
                "Succès",
                f"{count} employé(s) désactivé(s) dans\n{poly_nom}.")
            self.rafraichir()

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
