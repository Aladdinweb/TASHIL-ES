# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue Administration — Messagerie inter-polycliniques + Rollover
"""
import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import (
    get_connection, get_config, set_config)
from app.utils.deduction_engine import (
    executer_rollover_mai,
    verifier_rollover_necessaire)
from app.utils import polycliniques_dao
from app.views.dialogue_confirmation import (
    DialogueConfirmation)


class VueAdministration(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._piece_jointe = None
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        frame_titre = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad,
                         pady=(pad, 8))
        ctk.CTkLabel(
            frame_titre,
            text="Administration",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")

        # Infos nœud activé
        poly_nom = get_config("poly_nom") or "Non configuré"
        ctk.CTkLabel(
            frame_titre,
            text=f"🏥 {poly_nom}",
            font=POLICES["corps"],
            text_color=COULEURS["accent_bleu"]
        ).pack(side="right")

        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad,
                         pady=(0, 10))

        # Tabs internes
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COULEURS["bg_carte"],
            segmented_button_fg_color=COULEURS["bg_sidebar"],
            segmented_button_selected_color=COULEURS["accent_bleu"],
            segmented_button_unselected_color=COULEURS["bg_carte"],
            segmented_button_selected_hover_color=COULEURS["accent_bleu_clair"],
            text_color=COULEURS["texte_principal"],
            text_color_disabled=COULEURS["texte_discret"],
            corner_radius=8)
        self.tabview.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, pad))

        self.tabview.add("📤  Boîte d'envoi")
        self.tabview.add("📥  Boîte de réception")
        self.tabview.add("⚙  Rollover & Branches")

        self._construire_envoi(
            self.tabview.tab("📤  Boîte d'envoi"))
        self._construire_reception(
            self.tabview.tab("📥  Boîte de réception"))
        self._construire_rollover(
            self.tabview.tab("⚙  Rollover & Branches"))

    # ── Boîte d'envoi ─────────────────────────────────────
    def _construire_envoi(self, parent):
        pad = 16

        ctk.CTkLabel(
            parent,
            text="Envoyer un message / document",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", padx=pad, pady=(14, 8))

        def champ(label, placeholder="",
                  val_defaut=""):
            f = ctk.CTkFrame(parent,
                             fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 8))
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
            if val_defaut:
                e.insert(0, val_defaut)
            return e

        # Expéditeur auto depuis config
        exp_def = get_config(
            "expediteur_defaut") or "EPSP ES-SENIA"
        self.e_exp = champ(
            "Expéditeur (pré-rempli)",
            val_defaut=exp_def)

        # Destinataire
        f_dest = ctk.CTkFrame(parent,
                              fg_color="transparent")
        f_dest.pack(fill="x", padx=pad, pady=(0, 8))
        ctk.CTkLabel(
            f_dest, text="Destinataire (Polyclinique)",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        polys   = polycliniques_dao.lister_polycliniques()
        noms_p  = [p["nom"] for p in polys]
        self.m_dest = ctk.CTkOptionMenu(
            f_dest,
            values=noms_p if noms_p
            else ["Aucune polyclinique"],
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=36)
        self.m_dest.pack(fill="x", pady=(4, 0))

        self.e_objet = champ("Objet",
                             "Ex : Transmission dossier")
        self.e_corps = champ("Message",
                             "Corps du message…")

        # Pièce jointe
        f_pj = ctk.CTkFrame(parent,
                             fg_color="transparent")
        f_pj.pack(fill="x", padx=pad, pady=(0, 8))
        ctk.CTkLabel(
            f_pj, text="Pièce jointe",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        f_pj_row = ctk.CTkFrame(f_pj,
                                fg_color="transparent")
        f_pj_row.pack(fill="x", pady=(4, 0))

        self.lbl_pj = ctk.CTkLabel(
            f_pj_row,
            text="Aucun fichier sélectionné",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"])
        self.lbl_pj.pack(side="left",
                         fill="x", expand=True)

        ctk.CTkButton(
            f_pj_row, text="📎  Attacher",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"], height=34,
            corner_radius=DIMENSIONS["rayon_bouton"],
            width=110,
            command=self._choisir_fichier
        ).pack(side="right", padx=(8, 0))

        # Bouton envoyer
        ctk.CTkButton(
            parent,
            text="📤  Envoyer",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"], height=38,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._envoyer
        ).pack(fill="x", padx=pad,
               pady=(8, 14))

        # Liste messages envoyés
        ctk.CTkLabel(
            parent,
            text="Messages envoyés",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", padx=pad, pady=(8, 4))

        self.frame_envoyes = ctk.CTkScrollableFrame(
            parent,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=8, height=180,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_envoyes.pack(
            fill="x", padx=pad, pady=(0, 14))
        self._charger_envoyes()

    def _choisir_fichier(self):
        f = filedialog.askopenfilename(
            title="Choisir une pièce jointe",
            filetypes=[
                ("Tous fichiers", "*.*"),
                ("PDF", "*.pdf"),
                ("Excel", "*.xlsx"),
                ("Word", "*.docx"),
            ])
        if f:
            self._piece_jointe = f
            import os
            self.lbl_pj.configure(
                text=os.path.basename(f))

    def _envoyer(self):
        exp  = self.e_exp.get().strip()
        dest = self.m_dest.get()
        obj  = self.e_objet.get().strip()
        corp = self.e_corps.get().strip()

        if not dest or not obj:
            messagebox.showwarning(
                "Champs manquants",
                "Destinataire et objet obligatoires.")
            return
        conn = get_connection()
        conn.execute("""
            INSERT INTO messages
                (expediteur, destinataire, objet,
                 corps, piece_jointe, statut)
            VALUES (?,?,?,?,?,?)
        """, (exp, dest, obj, corp,
              self._piece_jointe or "", "envoye"))
        conn.commit()
        conn.close()
        messagebox.showinfo(
            "Message envoyé",
            f"✅ Message envoyé à {dest}.")
        self.e_objet.delete(0, "end")
        self.e_corps.delete(0, "end")
        self.lbl_pj.configure(
            text="Aucun fichier sélectionné")
        self._piece_jointe = None
        self._charger_envoyes()

    def _charger_envoyes(self):
        for w in self.frame_envoyes.winfo_children():
            w.destroy()
        exp = get_config(
            "expediteur_defaut") or "EPSP ES-SENIA"
        conn = get_connection()
        rows = conn.execute("""
            SELECT id, destinataire, objet,
                   statut, accuse_recu, created_at
            FROM messages
            WHERE expediteur = ?
            ORDER BY created_at DESC
            LIMIT 20
        """, (exp,)).fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.frame_envoyes,
                text="Aucun message envoyé.",
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=14)
            return

        for m in rows:
            f = ctk.CTkFrame(
                self.frame_envoyes,
                fg_color=COULEURS["bg_carte"],
                corner_radius=6)
            f.pack(fill="x", pady=2)

            f_top = ctk.CTkFrame(
                f, fg_color="transparent")
            f_top.pack(fill="x", padx=10, pady=(6, 2))

            ctk.CTkLabel(
                f_top,
                text=f"→ {m['destinataire']}  |  "
                     f"{m['objet']}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left")

            # Accusé de réception
            accuse = "✅ Reçu" if m["accuse_recu"] \
                     else "⏳ En attente"
            coul_a = (COULEURS["accent_vert"]
                      if m["accuse_recu"]
                      else COULEURS["accent_orange"])
            ctk.CTkLabel(
                f_top, text=accuse,
                font=POLICES["petit"],
                text_color=coul_a
            ).pack(side="right")

            ctk.CTkLabel(
                f, text=m["created_at"][:16],
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(anchor="w", padx=10,
                   pady=(0, 6))

    # ── Boîte de réception ────────────────────────────────
    def _construire_reception(self, parent):
        pad = 16
        ctk.CTkLabel(
            parent,
            text="Messages reçus",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", padx=pad, pady=(14, 8))

        ctk.CTkButton(
            parent, text="🔄  Actualiser",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"], height=32,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._charger_recus
        ).pack(anchor="e", padx=pad, pady=(0, 8))

        self.frame_recus = ctk.CTkScrollableFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_recus.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, 14))
        self._charger_recus()

    def _charger_recus(self):
        for w in self.frame_recus.winfo_children():
            w.destroy()
        dest = get_config("poly_nom") or ""
        conn = get_connection()
        rows = conn.execute("""
            SELECT id, expediteur, objet, corps,
                   piece_jointe, statut,
                   accuse_recu, created_at
            FROM messages
            WHERE destinataire LIKE ?
            ORDER BY created_at DESC
            LIMIT 30
        """, (f"%{dest}%",)).fetchall()

        # Marquer comme reçu
        conn.execute("""
            UPDATE messages SET statut='recu',
            accuse_recu=1
            WHERE destinataire LIKE ?
              AND statut='envoye'
        """, (f"%{dest}%",))
        conn.commit()
        conn.close()

        if not rows:
            ctk.CTkLabel(
                self.frame_recus,
                text="Aucun message reçu.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        for m in rows:
            f = ctk.CTkFrame(
                self.frame_recus,
                fg_color=COULEURS["bg_carte"],
                corner_radius=6)
            f.pack(fill="x", pady=3)

            f_top = ctk.CTkFrame(
                f, fg_color="transparent")
            f_top.pack(fill="x", padx=10,
                       pady=(8, 2))
            ctk.CTkLabel(
                f_top,
                text=f"✉  De : {m['expediteur']}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left")
            ctk.CTkLabel(
                f_top,
                text=m["created_at"][:16],
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(side="right")

            ctk.CTkLabel(
                f, text=f"Objet : {m['objet']}",
                font=POLICES["corps"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w", padx=10)

            if m.get("corps"):
                ctk.CTkLabel(
                    f, text=m["corps"][:120],
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"],
                    wraplength=400, justify="left"
                ).pack(anchor="w", padx=10,
                       pady=(2, 0))

            if m.get("piece_jointe"):
                import os
                nom_f = os.path.basename(
                    m["piece_jointe"])
                ctk.CTkLabel(
                    f, text=f"📎 {nom_f}",
                    font=POLICES["petit"],
                    text_color=COULEURS["accent_bleu"]
                ).pack(anchor="w", padx=10,
                       pady=(0, 8))

    # ── Rollover & Branches ───────────────────────────────
    def _construire_rollover(self, parent):
        from app.views.vue_rollover import VueRollover
        # Réutilise la vue rollover existante
        vue = VueRollover(parent)
        vue.pack(fill="both", expand=True)

    def rafraichir(self):
        for w in self.winfo_children():
            w.destroy()
        self._construire()
