# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Écran d'activation première utilisation — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import (
    set_config, chiffrer_code)

POLYCLINIQUES_CODES = [
    ("POLY_01", "POLYCLINIQUE ES SENIA"),
    ("POLY_02",
     "POLYCLINIQUE AADL AIN BEIDA MABROUK LOUCIF"),
    ("POLY_03", "POLYCLINIQUE AIN BEIDA 1"),
    ("POLY_04", "POLYCLINIQUE AIN BEIDA 2"),
    ("POLY_05", "POLYCLINIQUE SIDI MAAROUF"),
    ("POLY_06", "POLYCLINIQUE SIDI CHAHMI"),
    ("POLY_07", "POLYCLINIQUE EL KERMA"),
]


class VueActivation(ctk.CTkFrame):
    def __init__(self, parent,
                 on_activation_complete=None,
                 **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._callback = on_activation_complete
        self._construire()

    def _construire(self):
        # Centrage du contenu
        frame_centre = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_centre.place(
            relx=0.5, rely=0.5, anchor="center")

        # Drapeau
        ctk.CTkLabel(
            frame_centre, text="🇩🇿",
            font=("Segoe UI", 56)
        ).pack(pady=(0, 6))

        # Header officiel arabe
        ctk.CTkLabel(
            frame_centre,
            text="الجمهورية الجزائرية الديمقراطية الشعبية",
            font=("Segoe UI", 14, "bold"),
            text_color=COULEURS["texte_principal"],
            justify="center"
        ).pack()

        ctk.CTkLabel(
            frame_centre,
            text="وزارة الصحة",
            font=("Segoe UI", 12),
            text_color=COULEURS["texte_secondaire"],
            justify="center"
        ).pack(pady=(2, 14))

        # Emblème médical
        frame_emb = ctk.CTkFrame(
            frame_centre,
            fg_color=COULEURS["bg_carte"],
            corner_radius=14,
            border_width=2,
            border_color=COULEURS["accent_bleu"],
            width=380, height=86)
        frame_emb.pack(pady=(0, 18))
        frame_emb.pack_propagate(False)

        ctk.CTkLabel(
            frame_emb,
            text="⚕  EPSP ES-SENIA",
            font=("Segoe UI", 20, "bold"),
            text_color=COULEURS["accent_bleu"]
        ).place(relx=0.5, rely=0.36,
                anchor="center")

        ctk.CTkLabel(
            frame_emb,
            text="Gestionnaire de Reliquats "
                 "de Congé Annuel",
            font=("Segoe UI", 10),
            text_color=COULEURS["texte_secondaire"]
        ).place(relx=0.5, rely=0.72,
                anchor="center")

        # Titre activation
        ctk.CTkLabel(
            frame_centre,
            text="⚙  Première configuration",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            frame_centre,
            text="Sélectionnez votre polyclinique "
                 "pour activer ce poste.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(pady=(0, 14))

        # Dropdown polycliniques
        noms = [f"{code} — {nom}"
                for code, nom
                in POLYCLINIQUES_CODES]
        self.m_poly = ctk.CTkOptionMenu(
            frame_centre,
            values=noms,
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
            width=400, height=42,
            command=self._on_change)
        self.m_poly.pack(pady=(0, 4))
        self.m_poly.set(noms[0])

        # Affichage code sécurisé
        self.lbl_code = ctk.CTkLabel(
            frame_centre, text="",
            font=("Courier", 9),
            text_color=COULEURS["texte_discret"])
        self.lbl_code.pack(pady=(0, 14))
        self._on_change(noms[0])

        # Bouton activer
        self.btn_activer = ctk.CTkButton(
            frame_centre,
            text="🔓  Activer ce poste",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
            width=280, height=44,
            corner_radius=10,
            command=self._activer)
        self.btn_activer.pack(pady=(0, 10))

        # Erreur
        self.lbl_err = ctk.CTkLabel(
            frame_centre, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"])
        self.lbl_err.pack()

        # Footer
        ctk.CTkLabel(
            frame_centre,
            text="COPYRIGHT ILINE TECH 2026 "
                 "BY FERAK ALADDIN",
            font=("Segoe UI", 8),
            text_color=COULEURS["texte_discret"]
        ).pack(pady=(14, 0))

    def _on_change(self, val: str):
        code = val.split("—")[0].strip()
        h    = chiffrer_code(code)
        self.lbl_code.configure(
            text=f"Code sécurisé : {h[:16]}…")

    def _activer(self):
        self.lbl_err.configure(text="")
        sel  = self.m_poly.get()
        code = sel.split("—")[0].strip()
        nom  = (sel.split("—")[1].strip()
                if "—" in sel else sel)

        # Désactiver le bouton pendant le traitement
        self.btn_activer.configure(
            state="disabled",
            text="⏳  Activation…")

        try:
            set_config("activation_done", "1")
            set_config(
                "poly_code", chiffrer_code(code))
            set_config("poly_code_raw", code)
            set_config("poly_nom", nom)
            set_config(
                "expediteur_defaut",
                f"SERVICE {nom}")

            # Appeler le callback APRÈS
            # un court délai pour laisser
            # tkinter terminer l'update
            self.after(
                200,
                lambda: self._callback(code, nom)
                if self._callback else None)

        except Exception as ex:
            self.btn_activer.configure(
                state="normal",
                text="🔓  Activer ce poste")
            self.lbl_err.configure(
                text=f"Erreur : {str(ex)}")
