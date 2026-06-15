# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Génération des Bordereaux d'envoi — EPSP ES-SENIA
(Squelette — sera complété à l'étape 5)
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.widgets_import import BoutonAction, SeparateurH, TableauListe
from app.utils.database import get_connection


class VueBordereaux(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        frame_titre = ctk.CTkFrame(self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad, pady=(pad, 8))
        ctk.CTkLabel(frame_titre, text="Bordereaux d'envoi",
                     font=POLICES["titre_page"],
                     text_color=COULEURS["texte_principal"]).pack(side="left")
        BoutonAction(frame_titre, "＋  Nouveau bordereau",
                     style="primaire").pack(side="right")

        SeparateurH(self).pack(fill="x", padx=pad, pady=(0, pad))

        ctk.CTkLabel(self,
                     text="📄  La génération des bordereaux sera disponible à l'étape 5.",
                     font=POLICES["corps"],
                     text_color=COULEURS["texte_secondaire"]).pack(pady=40)

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
