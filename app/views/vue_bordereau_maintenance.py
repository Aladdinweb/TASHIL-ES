# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Bordereau — En maintenance
Ce module est temporairement suspendu.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class VueBordereauMaintenance(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        frame = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=16,
            border_width=2,
            border_color=COULEURS["accent_orange"])
        frame.place(relx=0.5, rely=0.5,
                    anchor="center")

        ctk.CTkLabel(
            frame, text="🔧",
            font=("Segoe UI", 64)
        ).pack(pady=(40, 8))

        ctk.CTkLabel(
            frame,
            text="هذا القسم قيد الصيانة حالياً",
            font=("Segoe UI", 16, "bold"),
            text_color=COULEURS["accent_orange"],
            justify="center"
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            frame,
            text="Ce module est actuellement "
                 "en maintenance.",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_secondaire"],
            justify="center"
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text="Le gabarit Excel officiel du "
                 "Bordereau d'envoi\n"
                 "sera intégré dès réception "
                 "du modèle papier.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_discret"],
            justify="center"
        ).pack(pady=(0, 30), padx=40)

        # ── GÉNÉRATION COMMENTÉE ─────────────────
        # TODO: Décommenter après réception
        #       du gabarit officiel EPSP.
        #
        # from app.reports.bordereau_excel import (
        #     generer_bordereau)
        # from app.utils.bordereaux_dao import (
        #     creer_bordereau, lister_bordereaux)
        #
        # def _generer():
        #     ...
        # ctk.CTkButton(frame, text="Générer",
        #     command=_generer).pack()

    def rafraichir(self):
        pass
