# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Dialogue transfert employé vers autre polyclinique"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.polycliniques_dao import lister_polycliniques
from app.utils.database import get_connection


class DialogueTransfert(ctk.CTkToplevel):
    def __init__(self, parent, emp: dict,
                 callback=None):
        super().__init__(parent)
        self._emp      = emp
        self._callback = callback
        self._polys    = lister_polycliniques()

        self.title("🔀  Transférer l'employé")
        self.configure(
            fg_color=COULEURS["bg_principal"])
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.geometry("440x280")
        self._construire()

    def _construire(self):
        f_head = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=52)
        f_head.pack(fill="x")
        f_head.pack_propagate(False)
        ctk.CTkLabel(
            f_head,
            text=f"Transférer : {self._emp['nom']} "
                 f"{self._emp['prenom']}",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=16)

        corps = ctk.CTkFrame(
            self, fg_color="transparent")
        corps.pack(
            fill="both", expand=True,
            padx=20, pady=16)

        ctk.CTkLabel(
            corps,
            text="Polyclinique de destination  *",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        noms = [p["nom"] for p in self._polys]
        self.m_dest = ctk.CTkOptionMenu(
            corps, values=noms,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=38)
        self.m_dest.pack(fill="x", pady=(4, 0))
        if noms:
            self.m_dest.set(noms[0])

        self.lbl_err = ctk.CTkLabel(
            corps, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"])
        self.lbl_err.pack(pady=(8, 0), anchor="w")

        f_pied = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=56)
        f_pied.pack(fill="x", side="bottom")
        f_pied.pack_propagate(False)

        ctk.CTkButton(
            f_pied, text="✕  Annuler",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_secondaire"],
            font=POLICES["bouton"],
            height=36, width=120,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(side="right", padx=(6, 16), pady=10)

        ctk.CTkButton(
            f_pied, text="🔀  Transférer",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=36, width=140,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._valider
        ).pack(side="right", padx=4, pady=10)

    def _valider(self):
        dest_nom = self.m_dest.get()
        poly = next(
            (p for p in self._polys
             if p["nom"] == dest_nom), None)
        if not poly:
            self.lbl_err.configure(
                text="Polyclinique invalide.")
            return
        conn = get_connection()
        conn.execute(
            "UPDATE employes "
            "SET polyclinique_id=?, "
            "updated_at=datetime('now','localtime') "
            "WHERE id=?",
            (poly["id"], self._emp["id"]))
        conn.commit()
        conn.close()
        if self._callback:
            self._callback()
        self.destroy()
