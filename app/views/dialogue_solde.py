# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Modifier le solde initial d'une année — EPSP ES-SENIA
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import conges_dao


class DialogueSolde(DialogueBase):
    """
    Permet d'ajuster les jours initiaux d'un solde existant
    ou d'en créer un nouveau pour une année donnée.
    """

    def __init__(self, parent, employe_data: dict,
                 solde_data: dict = None, callback_succes=None):
        self._emp      = employe_data
        self._solde    = solde_data
        self._callback = callback_succes
        mode = "Modifier le solde" if solde_data else "Nouveau solde"
        titre = f"{mode} — {employe_data['nom']} {employe_data['prenom']}"
        super().__init__(parent, titre=titre,
                         largeur=480, hauteur=400)

    def _construire_corps(self):
        pad = 20
        corps = self.frame_corps
        emp   = self._emp
        solde = self._solde

        # Info employé
        f_info = ctk.CTkFrame(corps,
                              fg_color=COULEURS["bg_carte"],
                              corner_radius=8)
        f_info.pack(fill="x", padx=pad, pady=(16, 12))

        def li(label, valeur):
            f = ctk.CTkFrame(f_info, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(f, text=label, font=POLICES["petit"],
                         text_color=COULEURS["texte_secondaire"],
                         width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=valeur, font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_principal"]).pack(
                             side="left")

        li("Employé :",  f"{emp['nom']} {emp['prenom']}")
        li("Grade :",    emp.get("grade", ""))
        if solde:
            li("Année :",    str(solde["annee"]))
            li("Utilisés :", f"{solde['jours_utilises']:.0f} j")

        # Année (uniquement en mode création)
        if not solde:
            f_annee = ctk.CTkFrame(corps, fg_color="transparent")
            f_annee.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(f_annee, text="Année  *",
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w")
            annees = [str(y) for y in range(
                datetime.date.today().year + 1,
                datetime.date.today().year - 6, -1)]
            self.m_annee = ctk.CTkOptionMenu(
                f_annee, values=annees,
                fg_color=COULEURS["bg_champ"],
                button_color=COULEURS["accent_bleu"],
                button_hover_color=COULEURS["accent_bleu_clair"],
                dropdown_fg_color=COULEURS["bg_carte"],
                dropdown_hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                dropdown_text_color=COULEURS["texte_principal"],
                font=POLICES["corps"], height=38,
                corner_radius=DIMENSIONS["rayon_bouton"])
            self.m_annee.pack(fill="x", pady=(4, 0))

        # Jours initiaux
        f_jours = ctk.CTkFrame(corps, fg_color="transparent")
        f_jours.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(f_jours, text="Jours initiaux  *",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        self.e_jours = ctk.CTkEntry(
            f_jours, placeholder_text="Ex : 30",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=38,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.e_jours.pack(fill="x", pady=(4, 0))

        if solde:
            self.e_jours.insert(0, str(int(solde["jours_initiaux"])))

        self._lbl_erreur = ctk.CTkLabel(
            corps, text="", font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)

        self.btn_valider.configure(text="Enregistrer")

    def _valider(self):
        self._cacher_erreur()
        try:
            jours = float(self.e_jours.get().strip().replace(",", "."))
            if jours <= 0:
                raise ValueError()
        except ValueError:
            self._afficher_erreur(
                "Entrez un nombre de jours valide (ex : 30).")
            return

        try:
            if self._solde:
                conges_dao.modifier_solde_initial(
                    self._solde["id"], jours)
                if self._callback:
                    self._callback({"action": "modifie"})
            else:
                annee = int(self.m_annee.get())
                conges_dao.creer_ou_obtenir_solde(
                    self._emp["id"], annee, jours)
                if self._callback:
                    self._callback({"action": "cree"})
            self.destroy()
        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")
