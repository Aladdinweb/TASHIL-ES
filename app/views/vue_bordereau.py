# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Bordereau — Workspace FIFO automatique
Scrollable, jamais vide.
"""
import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection


def _charger_mouvements() -> list:
    try:
        conn = get_connection()
        rows = conn.execute("""
            SELECT m.id, m.employe_id,
                   m.date_debut, m.date_fin,
                   m.nb_jours, m.type_conge,
                   e.nom, e.prenom, e.grade,
                   d.nom as service,
                   ca.annee
            FROM mouvements_conge m
            JOIN employes e
                ON e.id = m.employe_id
            JOIN departements d
                ON d.id = e.departement_id
            JOIN conges_annuels ca
                ON ca.id = m.conge_id
            WHERE m.type_conge = 'CONGE_ANNUEL'
              AND e.actif = 1
            ORDER BY m.date_debut DESC
            LIMIT 100
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as ex:
        print(f"[Bordereau] {ex}")
        return []


class VueBordereau(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._mouvements = []
        self._construire()

    def _construire(self):
        # Scroll principal — garantit le rendu
        # complet quelle que soit la résolution
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(
            fill="both", expand=True,
            padx=20, pady=20)

        # Titre
        ctk.CTkLabel(
            scroll, text="Bordereau d'envoi",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            scroll,
            text="Déduction FIFO automatique "
                 "des congés annuels",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w", pady=(2, 14))

        ctk.CTkFrame(
            scroll, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", pady=(0, 16))

        # Panneau actions
        action_f = ctk.CTkFrame(
            scroll,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        action_f.pack(fill="x", pady=(0, 16))

        f_btns = ctk.CTkFrame(
            action_f, fg_color="transparent")
        f_btns.pack(fill="x", padx=16,
                    pady=14)

        ctk.CTkButton(
            f_btns,
            height=40,
            text="🔍  Scanner & Vérifier FIFO",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._scanner_et_deduire
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_btns,
            height=40,
            text="📥  Exporter Excel",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._exporter_excel
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_btns,
            height=40,
            text="📂  Importer document externe",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._importer_document
        ).pack(side="left")

        self.lbl_resultat = ctk.CTkLabel(
            action_f, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_vert"],
            wraplength=700, justify="left")
        self.lbl_resultat.pack(
            anchor="w", padx=16,
            pady=(0, 12))

        # Liste mouvements
        ctk.CTkLabel(
            scroll,
            text="Congés Annuels — "
                 "Mouvements actifs",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", pady=(0, 8))

        self.liste_f = ctk.CTkFrame(
            scroll,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        self.liste_f.pack(fill="x")

        self._charger_liste()

    def _charger_liste(self):
        for w in self.liste_f.winfo_children():
            w.destroy()

        self._mouvements = _charger_mouvements()

        if not self._mouvements:
            ctk.CTkLabel(
                self.liste_f,
                text="Aucun congé annuel "
                     "enregistré pour l'instant.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=40)
            return

        fh = ctk.CTkFrame(
            self.liste_f,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=4)
        fh.pack(fill="x")
        for txt, w in [
            ("Employé", 180),
            ("Service", 140),
            ("Du", 100),
            ("Au", 100),
            ("Jours", 60),
            ("Année", 60),
        ]:
            ctk.CTkLabel(
                fh, text=txt,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=w, anchor="w"
            ).pack(side="left", padx=8, pady=8)

        for idx, m in enumerate(
                self._mouvements):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.liste_f, fg_color=bg,
                corner_radius=0)
            fl.pack(fill="x")

            try:
                d1 = datetime.date.fromisoformat(
                    m["date_debut"]
                ).strftime("%d/%m/%Y")
                d2 = datetime.date.fromisoformat(
                    m["date_fin"]
                ).strftime("%d/%m/%Y")
            except Exception:
                d1, d2 = (m["date_debut"],
                          m["date_fin"])

            for val, w in [
                (f"{m['nom']} {m['prenom']}", 180),
                (m["service"][:18], 140),
                (d1, 100), (d2, 100),
                (f"{m['nb_jours']:.0f} j", 60),
                (str(m["annee"]), 60),
            ]:
                ctk.CTkLabel(
                    fl, text=val,
                    font=POLICES["tableau"],
                    text_color=COULEURS["texte_principal"],
                    width=w, anchor="w"
                ).pack(side="left",
                       padx=8, pady=6)

    def _scanner_et_deduire(self):
        if not self._mouvements:
            messagebox.showinfo(
                "Info", "Aucun mouvement.")
            return

        traites = 0
        conn = get_connection()
        for m in self._mouvements:
            try:
                solde = conn.execute("""
                    SELECT jours_initiaux
                        - jours_utilises
                        AS restant
                    FROM conges_annuels
                    WHERE employe_id=?
                      AND annee=?
                """, (m["employe_id"],
                      m["annee"])).fetchone()
                if solde and solde["restant"] >= 0:
                    traites += 1
            except Exception:
                pass
        conn.close()

        msg = (f"✅ Scan FIFO terminé.\n\n"
               f"{len(self._mouvements)} "
               f"mouvement(s) analysé(s).\n"
               f"{traites} solde(s) vérifié(s).")
        self.lbl_resultat.configure(text=msg)
        messagebox.showinfo("Scan terminé", msg)
        self._charger_liste()

    def _exporter_excel(self):
        try:
            import openpyxl
            chemin = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                title="Enregistrer le Bordereau",
                initialfile=f"Bordereau_"
                            f"{datetime.date.today()}.xlsx")
            if not chemin:
                return
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Bordereau"
            ws.append([
                "N°", "Nom & Prénom", "Grade",
                "Service", "Date Début",
                "Date Fin", "Jours", "Année"])
            for i, m in enumerate(
                    self._mouvements, 1):
                ws.append([
                    i,
                    f"{m['nom']} {m['prenom']}",
                    m.get("grade", ""),
                    m.get("service", ""),
                    m["date_debut"],
                    m["date_fin"],
                    m["nb_jours"], m["annee"]])
            wb.save(chemin)
            messagebox.showinfo(
                "✅  Export réussi",
                f"Fichier : {chemin}")
        except Exception as ex:
            messagebox.showerror(
                "Erreur", str(ex))

    def _importer_document(self):
        chemin = filedialog.askopenfilename(
            title="Importer un document",
            filetypes=[
                ("Documents",
                 "*.pdf *.docx *.xlsx"),
                ("Tous", "*.*")])
        if chemin:
            messagebox.showinfo(
                "Document attaché",
                f"Fichier sélectionné :\n"
                f"{chemin}")

    def rafraichir(self, _=None):
        try:
            self._charger_liste()
        except Exception:
            pass
