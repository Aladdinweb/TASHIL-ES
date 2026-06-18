# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Tableau de Service — EPSP ES-SENIA
PLACEHOLDER — Architecture DB prête, UI en attente du
gabarit papier officiel.
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS


class VueTableauService(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        frame_titre = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad,
                         pady=(pad, 8))
        ctk.CTkLabel(
            frame_titre,
            text="Tableau de Service",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        ctk.CTkLabel(
            frame_titre,
            text="MODULE EN PRÉPARATION",
            font=POLICES["corps"],
            text_color=COULEURS["accent_orange"]
        ).pack(side="right")

        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad,
                         pady=(0, pad))

        # Zone placeholder centrale
        frame_center = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=16,
            border_width=2,
            border_color=COULEURS["accent_orange"])
        frame_center.pack(
            expand=True, padx=80, pady=40)

        ctk.CTkLabel(
            frame_center, text="📋",
            font=("Segoe UI", 64)
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            frame_center,
            text="Tableau de Service Mensuel",
            font=("Segoe UI", 18, "bold"),
            text_color=COULEURS["texte_principal"]
        ).pack()

        ctk.CTkLabel(
            frame_center,
            text="⏳  Placeholder : En attente du gabarit "
                 "papier officiel",
            font=POLICES["corps"],
            text_color=COULEURS["accent_orange"]
        ).pack(pady=(8, 4))

        ctk.CTkLabel(
            frame_center,
            text="La structure de la base de données est "
                 "prête.\n"
                 "La génération et l'export seront activés "
                 "après réception\n"
                 "du modèle de planning papier officiel.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"],
            justify="center"
        ).pack(pady=(0, 16))

        # Infos DB
        frame_db = ctk.CTkFrame(
            frame_center,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=8)
        frame_db.pack(
            padx=30, pady=(0, 30), fill="x")

        ctk.CTkLabel(
            frame_db,
            text="✅  Table `tableau_service` créée en DB",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_vert"]
        ).pack(pady=6)

        for info in [
            "Colonnes : employe_id, annee, mois, jour",
            "Types : Matin | Soir | Nuit | Garde | "
            "Repos | Congé | Absent",
            "Contrainte d'unicité par employé/jour/mois",
        ]:
            ctk.CTkLabel(
                frame_db,
                text=f"  • {info}",
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w", padx=14, pady=1)

        ctk.CTkFrame(
            frame_db, height=4,
            fg_color="transparent").pack()

        # ── LOGIQUE COMMENTÉE (en attente) ──────────────
        # TODO: Décommenter quand le gabarit papier
        #       est fourni.
        #
        # def generer_tableau_mensuel(annee, mois):
        #     """Génère le tableau de service mensuel."""
        #     pass
        #
        # def exporter_tableau_excel(annee, mois):
        #     """Exporte en Excel selon le gabarit."""
        #     pass
        #
        # def importer_depuis_gabarit(chemin_fichier):
        #     """Importe depuis un fichier gabarit."""
        #     pass

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
