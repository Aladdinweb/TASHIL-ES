# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Composants UI réutilisables — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class CarteStatistique(ctk.CTkFrame):
    """
    Carte affichant une statistique clé (chiffre + libellé + couleur accent).
    Utilisée dans le tableau de bord.
    """
    def __init__(self, parent, titre: str, valeur: str,
                 sous_texte: str = "", couleur_accent: str = None, **kwargs):
        couleur_accent = couleur_accent or COULEURS["accent_bleu"]
        super().__init__(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=DIMENSIONS["rayon_carte"],
            border_width=1,
            border_color=couleur_accent,
            **kwargs
        )
        self._couleur_accent = couleur_accent
        self._build(titre, valeur, sous_texte, couleur_accent)

    def _build(self, titre, valeur, sous_texte, couleur):
        # Bande colorée en haut
        bande = ctk.CTkFrame(self, height=4, fg_color=couleur,
                             corner_radius=0)
        bande.pack(fill="x", side="top")

        corps = ctk.CTkFrame(self, fg_color="transparent")
        corps.pack(fill="both", expand=True,
                   padx=DIMENSIONS["padding_carte"],
                   pady=DIMENSIONS["padding_carte"])

        ctk.CTkLabel(corps, text=titre,
                     font=POLICES["stat_label"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")

        self.lbl_valeur = ctk.CTkLabel(corps, text=valeur,
                                       font=POLICES["stat_chiffre"],
                                       text_color=COULEURS["texte_principal"])
        self.lbl_valeur.pack(anchor="w", pady=(2, 0))

        if sous_texte:
            ctk.CTkLabel(corps, text=sous_texte,
                         font=POLICES["petit"],
                         text_color=COULEURS["texte_discret"]).pack(anchor="w")

    def mettre_a_jour(self, valeur: str):
        self.lbl_valeur.configure(text=valeur)


class BoutonAction(ctk.CTkButton):
    """Bouton primaire standardisé."""
    def __init__(self, parent, texte: str, commande=None,
                 style: str = "primaire", **kwargs):
        styles = {
            "primaire": {
                "fg_color": COULEURS["accent_bleu"],
                "hover_color": COULEURS["accent_bleu_clair"],
                "text_color": "#FFFFFF",
            },
            "succes": {
                "fg_color": COULEURS["accent_vert"],
                "hover_color": "#059669",
                "text_color": "#FFFFFF",
            },
            "danger": {
                "fg_color": COULEURS["accent_rouge"],
                "hover_color": "#DC2626",
                "text_color": "#FFFFFF",
            },
            "neutre": {
                "fg_color": COULEURS["bg_champ"],
                "hover_color": COULEURS["bg_hover"],
                "text_color": COULEURS["texte_principal"],
            },
        }
        s = styles.get(style, styles["primaire"])
        super().__init__(
            parent,
            text=texte,
            command=commande,
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=36,
            **s,
            **kwargs
        )


class SeparateurH(ctk.CTkFrame):
    """Ligne de séparation horizontale."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=1,
                         fg_color=COULEURS["bordure"], **kwargs)


class TitreSection(ctk.CTkLabel):
    """Label titre de section."""
    def __init__(self, parent, texte: str, **kwargs):
        super().__init__(parent, text=texte,
                         font=POLICES["sous_titre"],
                         text_color=COULEURS["texte_principal"],
                         **kwargs)


class ChampSaisie(ctk.CTkEntry):
    """Champ de saisie stylisé."""
    def __init__(self, parent, placeholder: str = "", **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"],
            height=36,
            corner_radius=DIMENSIONS["rayon_bouton"],
            **kwargs
        )


class MenuDeroulant(ctk.CTkOptionMenu):
    """Menu déroulant stylisé."""
    def __init__(self, parent, valeurs: list, **kwargs):
        super().__init__(
            parent,
            values=valeurs,
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
            **kwargs
        )


class TableauListe(ctk.CTkScrollableFrame):
    """
    Tableau générique avec en-têtes et lignes alternées.
    Usage : TableauListe(parent, colonnes=[("Nom", 200), ("Grade", 150)])
    """
    def __init__(self, parent, colonnes: list, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=DIMENSIONS["rayon_carte"],
            scrollbar_button_color=COULEURS["accent_bleu"],
            **kwargs
        )
        self.colonnes = colonnes
        self._lignes = []
        self._construire_entetes()

    def _construire_entetes(self):
        frame_head = ctk.CTkFrame(self, fg_color=COULEURS["bg_sidebar"],
                                  corner_radius=0)
        frame_head.pack(fill="x", pady=(0, 2))

        for col_nom, col_larg in self.colonnes:
            ctk.CTkLabel(
                frame_head, text=col_nom,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=col_larg, anchor="w"
            ).pack(side="left", padx=8, pady=6)

    def vider(self):
        for widget in self._lignes:
            widget.destroy()
        self._lignes = []

    def ajouter_ligne(self, valeurs: list, on_click=None, tag: str = ""):
        idx = len(self._lignes)
        bg = COULEURS["bg_carte"] if idx % 2 == 0 else COULEURS["bg_champ"]

        frame_ligne = ctk.CTkFrame(self, fg_color=bg, corner_radius=0,
                                   cursor="hand2" if on_click else "arrow")
        frame_ligne.pack(fill="x", pady=1)

        for i, (col_nom, col_larg) in enumerate(self.colonnes):
            val = valeurs[i] if i < len(valeurs) else ""
            ctk.CTkLabel(
                frame_ligne, text=str(val),
                font=POLICES["tableau"],
                text_color=COULEURS["texte_principal"],
                width=col_larg, anchor="w"
            ).pack(side="left", padx=8, pady=5)

        if on_click:
            frame_ligne.bind("<Button-1>",
                             lambda e, t=tag: on_click(t))
            for child in frame_ligne.winfo_children():
                child.bind("<Button-1>",
                           lambda e, t=tag: on_click(t))

        # Effet hover
        def on_enter(e, f=frame_ligne):
            f.configure(fg_color=COULEURS["bg_hover"])
        def on_leave(e, f=frame_ligne, b=bg):
            f.configure(fg_color=b)

        frame_ligne.bind("<Enter>", on_enter)
        frame_ligne.bind("<Leave>", on_leave)
        for child in frame_ligne.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

        self._lignes.append(frame_ligne)
        return frame_ligne
