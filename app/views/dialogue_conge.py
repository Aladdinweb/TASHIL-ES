# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Enregistrement d'une prise de congé — EPSP ES-SENIA
Supporte : Congé Annuel, Dis-Intox, Semestre (MANIP-RADIO)
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import conges_dao

TYPES_CONGE = {
    "CONGE_ANNUEL": "Congé Annuel",
    "DIS_INTOX":    "Dis-Intox (protection radiation)",
    "SEMESTRE":     "Semestre (protection radiation)",
}


class DialogueConge(DialogueBase):
    """
    Formulaire d'enregistrement d'une prise de congé.
    - employe_data : dict avec id, nom, prenom, est_manip_radio, …
    - solde_data   : dict avec id (conge_id), annee, restant, …
    """

    def __init__(self, parent, employe_data: dict,
                 solde_data: dict, callback_succes=None):
        self._emp   = employe_data
        self._solde = solde_data
        self._callback = callback_succes
        titre = (f"Enregistrer un congé — "
                 f"{employe_data['nom']} {employe_data['prenom']}")
        super().__init__(parent, titre=titre,
                         largeur=560, hauteur=560)

    def _construire_corps(self):
        pad = 20
        corps = self.frame_corps
        emp   = self._emp
        solde = self._solde

        def sep(texte):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(14, 4))
            ctk.CTkLabel(f, text=texte, font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                             side="left", fill="x", expand=True, padx=(8, 0))

        # ── Récapitulatif employé ────────────────────────────
        sep("Récapitulatif")
        frame_recap = ctk.CTkFrame(corps,
                                   fg_color=COULEURS["bg_carte"],
                                   corner_radius=8)
        frame_recap.pack(fill="x", padx=pad, pady=(0, 4))

        def ligne_recap(label, valeur, couleur_val=None):
            f = ctk.CTkFrame(frame_recap, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(f, text=label, font=POLICES["petit"],
                         text_color=COULEURS["texte_secondaire"],
                         width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=valeur, font=POLICES["corps_bold"],
                         text_color=couleur_val or COULEURS["texte_principal"],
                         anchor="w").pack(side="left")

        ligne_recap("Employé :",
                    f"{emp['nom']} {emp['prenom']}")
        ligne_recap("Grade :",    emp.get("grade", ""))
        ligne_recap("Année :",    str(solde["annee"]))
        restant = solde["restant"]
        couleur_r = (COULEURS["accent_vert"] if restant > 10
                     else COULEURS["accent_orange"] if restant > 0
                     else COULEURS["accent_rouge"])
        ligne_recap("Solde restant :",
                    f"{restant:.0f} jour(s)", couleur_val=couleur_r)

        # ── Type de congé ────────────────────────────────────
        sep("Type de congé")
        types_disponibles = ["Congé Annuel"]
        if emp.get("est_manip_radio"):
            types_disponibles += [
                "Dis-Intox (protection radiation)",
                "Semestre (protection radiation)"
            ]

        f_type = ctk.CTkFrame(corps, fg_color="transparent")
        f_type.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(f_type, text="Type  *",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.m_type = ctk.CTkOptionMenu(
            f_type, values=types_disponibles,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], dropdown_font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"], height=38)
        self.m_type.pack(fill="x", pady=(4, 0))

        # ── Dates ────────────────────────────────────────────
        sep("Période du congé")

        frame_dates = ctk.CTkFrame(corps, fg_color="transparent")
        frame_dates.pack(fill="x", padx=pad, pady=(0, 10))
        frame_dates.columnconfigure(0, weight=1)
        frame_dates.columnconfigure(1, weight=1)

        def champ_date(parent_f, label, col):
            f = ctk.CTkFrame(parent_f, fg_color="transparent")
            f.grid(row=0, column=col,
                   padx=(0, 8) if col == 0 else (8, 0), sticky="ew")
            ctk.CTkLabel(f, text=label + "  *",
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
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

        # Calcul automatique à la saisie
        self.e_debut.bind("<FocusOut>", lambda e: self._calculer_jours())
        self.e_fin.bind("<FocusOut>",   lambda e: self._calculer_jours())

        # Affichage résultat calcul
        self.frame_calcul = ctk.CTkFrame(
            corps, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        self.frame_calcul.pack(fill="x", padx=pad, pady=(0, 10))

        self.lbl_calcul = ctk.CTkLabel(
            self.frame_calcul,
            text="Saisissez les dates pour calculer la durée.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_calcul.pack(pady=10, padx=12)

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

        # Label erreur
        self._lbl_erreur = ctk.CTkLabel(
            corps, text="", font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)

        # Bouton enregistrer renommé
        self.btn_valider.configure(text="Enregistrer le congé")

    def _parse_date(self, texte: str) -> datetime.date | None:
        texte = texte.strip()
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(texte, fmt).date()
            except ValueError:
                continue
        return None

    def _calculer_jours(self):
        d1 = self._parse_date(self.e_debut.get())
        d2 = self._parse_date(self.e_fin.get())
        if not d1 or not d2:
            return
        if d2 < d1:
            self.lbl_calcul.configure(
                text="⚠  La date de fin est antérieure à la date de début.",
                text_color=COULEURS["accent_rouge"])
            return
        nb = (d2 - d1).days + 1
        restant = self._solde["restant"]
        couleur = (COULEURS["accent_vert"] if nb <= restant
                   else COULEURS["accent_rouge"])
        self.lbl_calcul.configure(
            text=f"Durée calculée : {nb} jour(s)   |   "
                 f"Solde restant après : {restant - nb:.0f} jour(s)",
            text_color=couleur)
        self._nb_jours_calcules = nb

    def _type_interne(self, libelle: str) -> str:
        correspondance = {
            "Congé Annuel":                    "CONGE_ANNUEL",
            "Dis-Intox (protection radiation)":"DIS_INTOX",
            "Semestre (protection radiation)": "SEMESTRE",
        }
        return correspondance.get(libelle, "CONGE_ANNUEL")

    def _valider(self):
        self._cacher_erreur()

        d1 = self._parse_date(self.e_debut.get())
        d2 = self._parse_date(self.e_fin.get())

        if not d1:
            self._afficher_erreur(
                "Date de début invalide. Format attendu : JJ/MM/AAAA"); return
        if not d2:
            self._afficher_erreur(
                "Date de fin invalide. Format attendu : JJ/MM/AAAA"); return
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
            mouvement_id = conges_dao.enregistrer_mouvement(data)
            if self._callback:
                self._callback({"mouvement_id": mouvement_id,
                                "nb_jours": nb_jours})
            self.destroy()
        except ValueError as ex:
            self._afficher_erreur(str(ex))
        except Exception as ex:
            self._afficher_erreur(f"Erreur inattendue : {str(ex)}")
