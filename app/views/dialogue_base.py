# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Fenêtre modale de base réutilisable — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class DialogueBase(ctk.CTkToplevel):
    """
    Fenêtre modale générique.
    Sous-classer et implémenter _construire_corps() et _valider().
    """
    def __init__(self, parent, titre: str,
                 largeur: int = 540, hauteur: int = 520):
        super().__init__(parent)
        self.title(titre)
        self.configure(fg_color=COULEURS["bg_principal"])
        self.resizable(False, False)
        self.grab_set()          # Bloque la fenêtre parente
        self.focus_set()
        self.resultat = None     # Données retournées après validation

        # Centrer par rapport au parent
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - largeur) // 2
        y = py + (ph - hauteur) // 2
        self.geometry(f"{largeur}x{hauteur}+{x}+{y}")

        self._construire_structure(titre)
        self._construire_corps()
        self._construire_pied()

    def _construire_structure(self, titre: str):
        # Barre de titre personnalisée
        frame_titre = ctk.CTkFrame(self,
                                   fg_color=COULEURS["bg_sidebar"],
                                   corner_radius=0, height=56)
        frame_titre.pack(fill="x")
        frame_titre.pack_propagate(False)
        ctk.CTkLabel(frame_titre, text=titre,
                     font=POLICES["sous_titre"],
                     text_color=COULEURS["texte_principal"]).pack(
                         side="left", padx=20, pady=0)

        # Zone de corps (scrollable)
        self.frame_corps = ctk.CTkScrollableFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0,
            scrollbar_button_color=COULEURS["accent_bleu"]
        )
        self.frame_corps.pack(fill="both", expand=True)

    def _construire_pied(self):
        frame_pied = ctk.CTkFrame(self,
                                  fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=0, height=60)
        frame_pied.pack(fill="x", side="bottom")
        frame_pied.pack_propagate(False)

        ctk.CTkButton(
            frame_pied, text="Annuler",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            width=110, height=36,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(side="right", padx=(8, 16), pady=12)

        self.btn_valider = ctk.CTkButton(
            frame_pied, text="Enregistrer",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            width=130, height=36,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._valider
        )
        self.btn_valider.pack(side="right", padx=4, pady=12)

    def _construire_corps(self):
        """À implémenter dans les sous-classes."""
        raise NotImplementedError

    def _valider(self):
        """À implémenter dans les sous-classes."""
        raise NotImplementedError

    # ── Helpers ───────────────────────────────────────────────────
    def _ligne_label_champ(self, parent, label: str,
                           widget, obligatoire: bool = False):
        """Dispose un label au-dessus d'un widget de saisie."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 12))

        texte = label + ("  *" if obligatoire else "")
        ctk.CTkLabel(frame, text=texte,
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
        widget_reparente = widget(frame)
        widget_reparente.pack(fill="x", pady=(4, 0))
        return widget_reparente

    def _afficher_erreur(self, message: str):
        if hasattr(self, "_lbl_erreur"):
            self._lbl_erreur.configure(text=f"⚠  {message}")
            self._lbl_erreur.pack(fill="x", padx=20, pady=(0, 4))
        else:
            lbl = ctk.CTkLabel(
                self.frame_corps,
                text=f"⚠  {message}",
                font=POLICES["corps"],
                text_color=COULEURS["accent_rouge"],
                fg_color=("#3D1515" if True else "transparent"),
                corner_radius=6
            )
            lbl.pack(fill="x", padx=0, pady=(0, 8))
            self._lbl_erreur = lbl

    def _cacher_erreur(self):
        if hasattr(self, "_lbl_erreur"):
            self._lbl_erreur.pack_forget()
