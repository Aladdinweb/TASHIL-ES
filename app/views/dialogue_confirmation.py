# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue de confirmation générique — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class DialogueConfirmation(ctk.CTkToplevel):
    """
    Boîte de dialogue Oui / Non avec message configurable.
    Retourne True si l'utilisateur confirme, False sinon.
    """

    def __init__(self, parent, titre: str, message: str,
                 texte_confirmer: str = "Confirmer",
                 style_confirmer: str = "danger"):
        super().__init__(parent)
        self.title(titre)
        self.configure(fg_color=COULEURS["bg_principal"])
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.reponse = False

        largeur, hauteur = 420, 220
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - largeur) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - hauteur) // 2
        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")

        self._construire(titre, message, texte_confirmer, style_confirmer)

    def _construire(self, titre, message, texte_btn, style):
        couleurs_style = {
            "danger":  (COULEURS["accent_rouge"],  "#DC2626"),
            "succes":  (COULEURS["accent_vert"],   "#059669"),
            "primaire":(COULEURS["accent_bleu"],   COULEURS["accent_bleu_clair"]),
        }
        fg, hover = couleurs_style.get(style, couleurs_style["danger"])

        # Icône + message
        corps = ctk.CTkFrame(self, fg_color="transparent")
        corps.pack(fill="both", expand=True, padx=24, pady=24)

        icone = "⚠" if style == "danger" else "ℹ"
        ctk.CTkLabel(corps, text=icone, font=("Segoe UI", 32),
                     text_color=fg).pack(anchor="w")
        ctk.CTkLabel(corps, text=message,
                     font=POLICES["corps"],
                     text_color=COULEURS["texte_principal"],
                     wraplength=360, justify="left").pack(
                         anchor="w", pady=(8, 0))

        # Boutons
        frame_btns = ctk.CTkFrame(self, fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=0, height=56)
        frame_btns.pack(fill="x", side="bottom")
        frame_btns.pack_propagate(False)

        ctk.CTkButton(
            frame_btns, text="Annuler",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            width=100, height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(side="right", padx=(6, 16), pady=11)

        ctk.CTkButton(
            frame_btns, text=texte_btn,
            fg_color=fg, hover_color=hover,
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            width=120, height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._confirmer
        ).pack(side="right", padx=4, pady=11)

    def _confirmer(self):
        self.reponse = True
        self.destroy()
