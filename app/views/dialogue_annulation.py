# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Annulation totale ou Interruption
partielle d'un congé — EPSP ES-SENIA
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils import conges_dao


class DialogueAnnulation(ctk.CTkToplevel):
    def __init__(self, parent, mouvement: dict,
                 callback_succes=None):
        super().__init__(parent)
        self._mouvement  = mouvement
        self._callback   = callback_succes

        self.title("Annuler / Interrompre un congé")
        self.configure(fg_color=COULEURS["bg_principal"])
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        w, h = 520, 460
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._construire()

    def _construire(self):
        m   = self._mouvement
        pad = 20

        # En-tête
        fh = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=52)
        fh.pack(fill="x")
        fh.pack_propagate(False)
        ctk.CTkLabel(
            fh,
            text="Annuler / Interrompre un congé",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left", padx=pad)

        # Corps scrollable
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Info congé
        try:
            d1 = datetime.date.fromisoformat(
                m["date_debut"]).strftime("%d/%m/%Y")
            d2 = datetime.date.fromisoformat(
                m["date_fin"]).strftime("%d/%m/%Y")
        except Exception:
            d1, d2 = m.get("date_debut",""), \
                     m.get("date_fin","")

        today = datetime.date.today()
        try:
            date_fin_obj = datetime.date.fromisoformat(
                m["date_fin"])
            jours_restants = max(
                0, (date_fin_obj - today).days + 1)
        except Exception:
            jours_restants = 0

        fi = ctk.CTkFrame(
            scroll, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        fi.pack(fill="x", padx=pad,
                pady=(14, 10))

        for label, valeur in [
            ("Employé",
             f"{m.get('nom','')} "
             f"{m.get('prenom','')}"),
            ("Période",     f"Du {d1} au {d2}"),
            ("Durée totale",
             f"{m.get('nb_jours',0):.0f} jour(s)"),
            ("Aujourd'hui", today.strftime("%d/%m/%Y")),
            ("Jours non utilisés",
             f"{jours_restants} jour(s)"),
        ]:
            f = ctk.CTkFrame(fi,
                             fg_color="transparent")
            f.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                f, text=label + " :",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"],
                width=160, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                f, text=valeur,
                font=POLICES["corps"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left")

        # Option A — Interruption partielle
        ctk.CTkLabel(
            scroll,
            text="Option A — Interruption partielle",
            font=POLICES["sous_titre"],
            text_color=COULEURS["accent_orange"]
        ).pack(anchor="w", padx=pad,
               pady=(10, 4))

        fa = ctk.CTkFrame(
            scroll, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        fa.pack(fill="x", padx=pad, pady=(0, 10))

        ctk.CTkLabel(
            fa,
            text="Date de retour effectif :",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w", padx=12, pady=(10, 4))

        f_date = ctk.CTkFrame(
            fa, fg_color="transparent")
        f_date.pack(fill="x", padx=12,
                    pady=(0, 6))
        self.e_date_inter = ctk.CTkEntry(
            f_date,
            placeholder_text="JJ/MM/AAAA",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"],
            height=34, width=140,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.e_date_inter.pack(side="left")
        self.e_date_inter.insert(
            0, today.strftime("%d/%m/%Y"))

        ctk.CTkButton(
            fa,
            text="⚡  Interrompre",
            fg_color=COULEURS["accent_orange"],
            hover_color="#D97706",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._interrompre
        ).pack(fill="x", padx=12,
               pady=(4, 12))

        # Option B — Annulation totale
        ctk.CTkLabel(
            scroll,
            text="Option B — Annulation totale",
            font=POLICES["sous_titre"],
            text_color=COULEURS["accent_rouge"]
        ).pack(anchor="w", padx=pad,
               pady=(4, 4))

        fb = ctk.CTkFrame(
            scroll, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        fb.pack(fill="x", padx=pad, pady=(0, 10))

        ctk.CTkLabel(
            fb,
            text=f"Restitue "
                 f"{m.get('nb_jours',0):.0f} j "
                 f"au solde.",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w", padx=12,
               pady=(10, 6))

        ctk.CTkButton(
            fb,
            text=f"🗑  Annuler totalement",
            fg_color=COULEURS["accent_rouge"],
            hover_color="#DC2626",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._annuler_total
        ).pack(fill="x", padx=12,
               pady=(0, 12))

        # Label erreur
        self.lbl_err = ctk.CTkLabel(
            scroll, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"])
        self.lbl_err.pack(padx=pad)

        # Pied
        fp = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=52)
        fp.pack(fill="x", side="bottom")
        fp.pack_propagate(False)
        ctk.CTkButton(
            fp, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=110,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(side="right", padx=16, pady=9)

    def _parse_date(self, texte: str):
        for fmt in ("%d/%m/%Y",
                    "%d-%m-%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(
                    texte.strip(), fmt).date()
            except ValueError:
                continue
        return None

    def _interrompre(self):
        self.lbl_err.configure(text="")
        d = self._parse_date(
            self.e_date_inter.get())
        if not d:
            self.lbl_err.configure(
                text="Date invalide (JJ/MM/AAAA).")
            return
        try:
            res = conges_dao.interrompre_mouvement(
                self._mouvement["id"],
                d.isoformat())
            from tkinter import messagebox
            messagebox.showinfo(
                "Interruption effectuée",
                f"✅ Congé interrompu.\n"
                f"Jours restitués : "
                f"{res['jours_restitues']:.0f} j\n"
                f"Reliquat {res['annee']}.")
            if self._callback:
                self._callback(res)
            self.destroy()
        except ValueError as ex:
            self.lbl_err.configure(text=str(ex))
        except Exception as ex:
            self.lbl_err.configure(
                text=f"Erreur : {str(ex)}")

    def _annuler_total(self):
        from tkinter import messagebox
        nb = self._mouvement.get("nb_jours", 0)
        rep = messagebox.askyesno(
            "Confirmer",
            f"Annuler ce congé de {nb:.0f} j ?\n"
            "Tous les jours seront restitués.")
        if not rep:
            return
        try:
            res = conges_dao.annuler_mouvement_total(
                self._mouvement["id"])
            messagebox.showinfo(
                "Annulation effectuée",
                f"✅ {res['jours_restitues']:.0f} j "
                f"restitués au reliquat "
                f"{res['annee']}.")
            if self._callback:
                self._callback(res)
            self.destroy()
        except Exception as ex:
            self.lbl_err.configure(
                text=f"Erreur : {str(ex)}")
