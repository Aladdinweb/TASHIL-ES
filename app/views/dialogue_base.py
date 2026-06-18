# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Fenêtre modale de base — boutons Enregistrer/Annuler garantis visibles
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class DialogueBase(ctk.CTkToplevel):
    def __init__(self, parent, titre: str,
                 largeur=560, hauteur=600):
        super().__init__(parent)
        self.title(titre)
        self.configure(fg_color=COULEURS["bg_principal"])
        self.resizable(True, False)
        self.grab_set()
        self.focus_set()
        self.resultat = None

        # Centrer
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x  = px + (pw - largeur) // 2
        y  = py + (ph - hauteur) // 2
        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")

        # Layout : titre + corps scrollable + pied FIXE
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._construire_barre_titre(titre)
        self._construire_zone_corps()
        self._construire_pied_fixe()
        self._construire_corps()

    def _construire_barre_titre(self, titre):
        frame = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=52)
        frame.grid(row=0, column=0, sticky="ew")
        frame.grid_propagate(False)
        ctk.CTkLabel(
            frame, text=titre,
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=20)

    def _construire_zone_corps(self):
        self.frame_corps = ctk.CTkScrollableFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_corps.grid(
            row=1, column=0, sticky="nsew")

    def _construire_pied_fixe(self):
        """
        Pied TOUJOURS visible — ne défile pas.
        Contient Annuler + Enregistrer.
        """
        frame_pied = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=64)
        frame_pied.grid(row=2, column=0, sticky="ew")
        frame_pied.grid_propagate(False)

        # Bouton Annuler
        ctk.CTkButton(
            frame_pied,
            text="✕  Annuler",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"],
            width=130, height=38,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(side="right", padx=(6, 16), pady=13)

        # Bouton Enregistrer (référence pour personnalisation)
        self.btn_valider = ctk.CTkButton(
            frame_pied,
            text="💾  Enregistrer",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            width=180, height=38,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._valider
        )
        self.btn_valider.pack(
            side="right", padx=4, pady=13)

    def _construire_corps(self):
        raise NotImplementedError

    def _valider(self):
        raise NotImplementedError

    def _afficher_erreur(self, message: str):
        if hasattr(self, "_lbl_erreur"):
            self._lbl_erreur.configure(
                text=f"⚠  {message}")
            self._lbl_erreur.pack(
                fill="x", padx=20, pady=(0, 4))

    def _cacher_erreur(self):
        if hasattr(self, "_lbl_erreur"):
            self._lbl_erreur.pack_forget()
