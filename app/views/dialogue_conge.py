# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Enregistrement d'une prise de congé — EPSP ES-SENIA
Affiche le plan de déduction prioritaire avant confirmation.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import conges_dao


class DialogueConge(DialogueBase):
    def __init__(self, parent, employe_data: dict,
                 solde_data: dict, callback_succes=None):
        self._emp      = employe_data
        self._solde    = solde_data
        self._callback = callback_succes
        self._nb_jours_calcules = 0
        titre = (f"Enregistrer un congé — "
                 f"{employe_data['nom']} {employe_data['prenom']}")
        super().__init__(parent, titre=titre,
                         largeur=580, hauteur=620)

    def _construire_corps(self):
        pad = 20
        corps = self.frame_corps
        emp   = self._emp

        def sep(texte):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(14, 4))
            ctk.CTkLabel(f, text=texte, font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                         side="left", fill="x", expand=True, padx=(8, 0))

        # ── Récapitulatif soldes disponibles ─────────────────
        sep("Soldes disponibles (ordre de déduction)")
        frame_soldes = ctk.CTkFrame(corps,
                                    fg_color=COULEURS["bg_carte"],
                                    corner_radius=8)
        frame_soldes.pack(fill="x", padx=pad, pady=(0, 6))

        soldes_ordonnes = conges_dao.obtenir_soldes_ordonnes(
            emp["id"]) if hasattr(conges_dao, 'obtenir_soldes_ordonnes') \
            else []

        # Import direct du moteur
        from app.utils.deduction_engine import obtenir_soldes_ordonnes
        soldes_ordonnes = obtenir_soldes_ordonnes(emp["id"])
        total_dispo = sum(s["restant"] for s in soldes_ordonnes)

        if soldes_ordonnes:
            for idx, s in enumerate(soldes_ordonnes):
                f = ctk.CTkFrame(frame_soldes, fg_color="transparent")
                f.pack(fill="x", padx=12, pady=3)
                priorite = f"{'①②③④⑤'[idx] if idx < 5 else str(idx+1)}"
                coul = (COULEURS["accent_orange"]
                        if s["annee"] < datetime.date.today().year
                        else COULEURS["accent_vert"])
                ctk.CTkLabel(f,
                             text=f"{priorite}  {s['annee']}",
                             font=POLICES["corps_bold"],
                             text_color=coul,
                             width=100, anchor="w").pack(side="left")
                ctk.CTkLabel(f,
                             text=f"{s['restant']:.0f} j disponibles",
                             font=POLICES["corps"],
                             text_color=COULEURS["texte_principal"]).pack(
                                 side="left")
                if idx == 0 and len(soldes_ordonnes) > 1:
                    ctk.CTkLabel(f, text="← prioritaire",
                                 font=POLICES["petit"],
                                 text_color=COULEURS["accent_orange"]).pack(
                                     side="left", padx=(8, 0))
        else:
            ctk.CTkLabel(frame_soldes,
                         text="Aucun solde disponible.",
                         font=POLICES["corps"],
                         text_color=COULEURS["accent_rouge"]).pack(pady=8)

        # Total
        f_total = ctk.CTkFrame(frame_soldes, fg_color="transparent")
        f_total.pack(fill="x", padx=12, pady=(4, 8))
        ctk.CTkFrame(frame_soldes, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=12, pady=(0, 6))
        ctk.CTkLabel(frame_soldes,
                     text=f"TOTAL DISPONIBLE : {total_dispo:.0f} jour(s)",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_principal"]).pack(
                         padx=12, pady=(0, 8), anchor="w")

        # ── Type de congé ─────────────────────────────────────
        sep("Type & Période")
        types_dispo = ["Congé Annuel"]
        if emp.get("est_manip_radio"):
            types_dispo += [
                "Dis-Intox (protection radiation)",
                "Semestre (protection radiation)"
            ]

        f_type = ctk.CTkFrame(corps, fg_color="transparent")
        f_type.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(f_type, text="Type  *",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.m_type = ctk.CTkOptionMenu(
            f_type, values=types_dispo,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=38,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.m_type.pack(fill="x", pady=(4, 0))

        # Dates côte à côte
        frame_dates = ctk.CTkFrame(corps, fg_color="transparent")
        frame_dates.pack(fill="x", padx=pad, pady=(0, 10))
        frame_dates.columnconfigure(0, weight=1)
        frame_dates.columnconfigure(1, weight=1)

        def champ_date(parent_f, label, col):
            f = ctk.CTkFrame(parent_f, fg_color="transparent")
            f.grid(row=0, column=col,
                   padx=(0, 6) if col == 0 else (6, 0), sticky="ew")
            ctk.CTkLabel(f, text=label + "  *",
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w")
            e = ctk.CTkEntry(
                f, placeholder_text="JJ/MM/AAAA",
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"], height=38,
                corner_radius=DIMENSIONS["rayon_bouton"])
            e.pack(fill="x", pady=(4, 0))
            return e

        self.e_debut = champ_date(frame_dates, "Du (date début)", 0)
        self.e_fin   = champ_date(frame_dates, "Au (date fin)",   1)
        self.e_debut.bind("<FocusOut>", lambda e: self._calculer_et_apercu())
        self.e_fin.bind("<FocusOut>",   lambda e: self._calculer_et_apercu())

        # ── Zone aperçu déduction ─────────────────────────────
        sep("Aperçu de la déduction automatique")
        self.frame_apercu = ctk.CTkFrame(corps,
                                          fg_color=COULEURS["bg_carte"],
                                          corner_radius=8)
        self.frame_apercu.pack(fill="x", padx=pad, pady=(0, 10))
        self.lbl_apercu = ctk.CTkLabel(
            self.frame_apercu,
            text="Saisissez les dates pour voir la répartition.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_apercu.pack(pady=10, padx=12)

        # Observation
        f_obs = ctk.CTkFrame(corps, fg_color="transparent")
        f_obs.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(f_obs, text="Observation (optionnel)",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.e_obs = ctk.CTkEntry(
            f_obs, placeholder_text="Ex : Congé estival 2025",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=38,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.e_obs.pack(fill="x", pady=(4, 0))

        self._lbl_erreur = ctk.CTkLabel(
            corps, text="", font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)

        self.btn_valider.configure(text="Enregistrer le congé")

        # Désactiver si aucun solde
        if not soldes_ordonnes:
            self.btn_valider.configure(state="disabled")

    def _parse_date(self, texte: str):
        texte = texte.strip()
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(texte, fmt).date()
            except ValueError:
                continue
        return None

    def _calculer_et_apercu(self):
        d1 = self._parse_date(self.e_debut.get())
        d2 = self._parse_date(self.e_fin.get())
        if not d1 or not d2:
            return
        if d2 < d1:
            self.lbl_apercu.configure(
                text="⚠  Date de fin antérieure à la date de début.",
                text_color=COULEURS["accent_rouge"])
            return

        nb = (d2 - d1).days + 1
        self._nb_jours_calcules = nb

        # Calculer le plan de déduction
        plan = conges_dao.apercu_deduction(self._emp["id"], nb)

        # Vider l'aperçu
        for w in self.frame_apercu.winfo_children():
            w.destroy()

        if plan is None:
            total = conges_dao.total_disponible(self._emp["id"])
            ctk.CTkLabel(
                self.frame_apercu,
                text=f"⚠  Solde insuffisant : {total:.0f} j dispo, "
                     f"{nb} j demandés.",
                font=POLICES["corps"],
                text_color=COULEURS["accent_rouge"]).pack(
                    pady=10, padx=12)
            return

        # Afficher le plan ligne par ligne
        f_titre = ctk.CTkFrame(self.frame_apercu,
                                fg_color="transparent")
        f_titre.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(f_titre,
                     text=f"Durée : {nb} jour(s)  |  "
                          f"Répartition sur {len(plan)} reliquat(s) :",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_principal"]).pack(
                         anchor="w")

        for tranche in plan:
            f_t = ctk.CTkFrame(self.frame_apercu,
                               fg_color="transparent")
            f_t.pack(fill="x", padx=12, pady=2)
            coul = (COULEURS["accent_orange"]
                    if tranche["annee"] < datetime.date.today().year
                    else COULEURS["accent_vert"])
            ctk.CTkLabel(
                f_t,
                text=f"  Reliquat {tranche['annee']} : "
                     f"−{tranche['jours_a_deduire']:.0f} j",
                font=POLICES["corps"],
                text_color=coul).pack(anchor="w")

        ctk.CTkFrame(self.frame_apercu, height=4,
                     fg_color="transparent").pack()

    def _type_interne(self, libelle: str) -> str:
        return {
            "Congé Annuel":                    "CONGE_ANNUEL",
            "Dis-Intox (protection radiation)":"DIS_INTOX",
            "Semestre (protection radiation)": "SEMESTRE",
        }.get(libelle, "CONGE_ANNUEL")

    def _valider(self):
        self._cacher_erreur()
        d1 = self._parse_date(self.e_debut.get())
        d2 = self._parse_date(self.e_fin.get())

        if not d1:
            self._afficher_erreur(
                "Date de début invalide (JJ/MM/AAAA)."); return
        if not d2:
            self._afficher_erreur(
                "Date de fin invalide (JJ/MM/AAAA)."); return
        if d2 < d1:
            self._afficher_erreur(
                "La date de fin doit être >= à la date de début."); return

        nb_jours = (d2 - d1).days + 1
        data = {
            "employe_id": self._emp["id"],
            "conge_id":   self._solde["id"],
            "type_conge": self._type_interne(self.m_type.get()),
            "date_debut": d1.isoformat(),
            "date_fin":   d2.isoformat(),
            "nb_jours":   nb_jours,
            "observation":self.e_obs.get().strip(),
        }
        try:
            mouvements = conges_dao.enregistrer_mouvement(data)
            if self._callback:
                self._callback({"mouvements": mouvements,
                                "nb_jours": nb_jours})
            self.destroy()
        except ValueError as ex:
            self._afficher_erreur(str(ex))
        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")
