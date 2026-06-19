# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue congé rapide depuis le menu contextuel.
Maladie/Maternité : enregistre SANS déduire le reliquat.
Congé Annuel : FIFO déduction.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection
from app.utils.deduction_engine import (
    enregistrer_conge_prioritaire)

TYPES = {
    "CONGE_ANNUEL": ("📅", "Congé Annuel",
                     True,  COULEURS["accent_bleu"]),
    "MALADIE":      ("🏥", "Congé Maladie",
                     False, "#EF4444"),
    "MATERNITE":    ("👶", "Maternité / Autre",
                     False, "#8B5CF6"),
}


class DialogueCongeRapide(ctk.CTkToplevel):
    def __init__(self, parent, emp: dict,
                 type_conge: str = "CONGE_ANNUEL",
                 callback=None):
        super().__init__(parent)
        self._emp      = emp
        self._type     = type_conge
        self._callback = callback
        icone, label, deduit, coul = TYPES.get(
            type_conge, TYPES["CONGE_ANNUEL"])

        self.title(f"{icone}  {label}")
        self.configure(
            fg_color=COULEURS["bg_principal"])
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        w, h = 480, 420
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._deduit = deduit
        self._coul   = coul
        self._construire(icone, label, coul)

    def _construire(self, icone, label, coul):
        # En-tête
        f_head = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=56)
        f_head.pack(fill="x")
        f_head.pack_propagate(False)
        ctk.CTkLabel(
            f_head,
            text=f"{icone}  {label}  —  "
                 f"{self._emp['nom']} "
                 f"{self._emp['prenom']}",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=16)

        # Corps
        frame = ctk.CTkFrame(
            self, fg_color="transparent")
        frame.pack(
            fill="both", expand=True,
            padx=20, pady=16)

        # Avertissement si pas de déduction
        if not self._deduit:
            ctk.CTkFrame(
                frame,
                fg_color="#1A1A2E",
                corner_radius=6,
                border_width=1,
                border_color=coul
            ).pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(
                frame,
                text="ℹ️  Ce type de congé ne déduit "
                     "PAS le reliquat annuel.",
                font=POLICES["corps"],
                text_color=coul
            ).pack(anchor="w", pady=(0, 12))

        def champ(label, placeholder=""):
            f = ctk.CTkFrame(frame,
                             fg_color="transparent")
            f.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(
                f, text=label,
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w")
            e = ctk.CTkEntry(
                f, placeholder_text=placeholder,
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"], height=36,
                corner_radius=DIMENSIONS["rayon_bouton"])
            e.pack(fill="x", pady=(4, 0))
            return e

        self.e_debut = champ(
            "Date début  *", "JJ/MM/AAAA")
        self.e_fin   = champ(
            "Date fin  *",   "JJ/MM/AAAA")
        self.e_motif = champ(
            "Motif / Justification",
            "Ex : Repos médical prescrit")

        # Label calcul
        self.lbl_calc = ctk.CTkLabel(
            frame, text="",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"])
        self.lbl_calc.pack(anchor="w",
                           pady=(0, 8))

        self.e_debut.bind(
            "<FocusOut>", lambda e: self._calc())
        self.e_fin.bind(
            "<FocusOut>", lambda e: self._calc())

        # Erreur
        self.lbl_err = ctk.CTkLabel(
            frame, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"])
        self.lbl_err.pack(anchor="w")

        # Pied — boutons fixes
        f_pied = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=58)
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
        ).pack(side="right", padx=(6, 16), pady=11)

        ctk.CTkButton(
            f_pied, text="💾  Enregistrer",
            fg_color=coul,
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=36, width=160,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._valider
        ).pack(side="right", padx=4, pady=11)

    def _parse(self, texte: str):
        for fmt in ("%d/%m/%Y",
                    "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(
                    texte.strip(), fmt).date()
            except ValueError:
                continue
        return None

    def _calc(self):
        d1 = self._parse(self.e_debut.get())
        d2 = self._parse(self.e_fin.get())
        if d1 and d2 and d2 >= d1:
            nb = (d2 - d1).days + 1
            self.lbl_calc.configure(
                text=f"Durée calculée : {nb} jour(s)")

    def _valider(self):
        self.lbl_err.configure(text="")
        d1 = self._parse(self.e_debut.get())
        d2 = self._parse(self.e_fin.get())

        if not d1:
            self.lbl_err.configure(
                text="Date début invalide."); return
        if not d2:
            self.lbl_err.configure(
                text="Date fin invalide."); return
        if d2 < d1:
            self.lbl_err.configure(
                text="Date fin < date début."); return

        nb = (d2 - d1).days + 1
        motif = self.e_motif.get().strip()

        try:
            if self._deduit:
                # FIFO déduction reliquat
                enregistrer_conge_prioritaire(
                    employe_id=self._emp["id"],
                    nb_jours=nb,
                    date_debut=d1.isoformat(),
                    date_fin=d2.isoformat(),
                    type_conge=self._type,
                    observation=motif)
            else:
                # Enregistrement sans déduction
                conn = get_connection()
                # Trouver ou créer un solde
                annee = d1.year
                row = conn.execute(
                    "SELECT id FROM conges_annuels "
                    "WHERE employe_id=? AND annee=?",
                    (self._emp["id"], annee)
                ).fetchone()
                if not row:
                    conn.execute("""
                        INSERT INTO conges_annuels
                            (employe_id, annee,
                             jours_initiaux,
                             jours_utilises)
                        VALUES (?,?,0,0)
                    """, (self._emp["id"], annee))
                    conn.commit()
                    row = conn.execute(
                        "SELECT id FROM conges_annuels "
                        "WHERE employe_id=? AND annee=?",
                        (self._emp["id"], annee)
                    ).fetchone()
                conn.execute("""
                    INSERT INTO mouvements_conge
                        (employe_id, conge_id,
                         type_conge, date_debut,
                         date_fin, nb_jours,
                         motif, observation)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (
                    self._emp["id"], row["id"],
                    self._type,
                    d1.isoformat(), d2.isoformat(),
                    nb, motif,
                    "Sans déduction reliquat"))
                conn.commit()
                conn.close()

            if self._callback:
                self._callback()
            self.destroy()

        except ValueError as ex:
            self.lbl_err.configure(text=str(ex))
        except Exception as ex:
            self.lbl_err.configure(
                text=f"Erreur: {str(ex)}")
