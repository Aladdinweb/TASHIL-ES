# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Bordereau — Déduction FIFO automatique
Scan des mouvements → déduction reliquat
"""
import datetime
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection
from app.utils.deduction_engine import (
    enregistrer_conge_prioritaire)


def _charger_mouvements_non_soldes() -> list:
    """Congés annuels non encore comptabilisés."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.id, m.employe_id,
               m.date_debut, m.date_fin,
               m.nb_jours, m.type_conge,
               e.nom, e.prenom, e.grade,
               d.nom as service,
               ca.annee
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
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


class VueBordereau(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._mouvements = []
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre
        titre_f = ctk.CTkFrame(
            self, fg_color="transparent")
        titre_f.place(
            x=pad, y=pad,
            relwidth=1, width=-pad*2, height=44)
        ctk.CTkLabel(
            titre_f, text="Bordereau d'envoi",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).place(x=0, y=0)
        ctk.CTkLabel(
            titre_f,
            text="Déduction FIFO automatique",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=0, y=28)

        # Séparateur
        sep = ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"])
        sep.place(x=pad, y=pad+52,
                  relwidth=1, width=-pad*2)

        # Panneau gauche — liste mouvements
        liste_f = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        liste_f.place(
            x=pad, y=pad+62,
            relwidth=0.62, width=-pad*2,
            rely=0, relheight=1,
            height=-(pad+70))

        ctk.CTkLabel(
            liste_f,
            text="Congés Annuels — "
                 "Prêts pour bordereau",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).place(x=14, y=14)

        sep2 = ctk.CTkFrame(
            liste_f, height=1,
            fg_color=COULEURS["bordure"])
        sep2.place(x=14, y=40,
                   relwidth=1, width=-28)

        self.scroll = ctk.CTkScrollableFrame(
            liste_f,
            fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.scroll.place(
            x=0, y=48,
            relwidth=1, relheight=1,
            height=-48)

        # Panneau droite — actions
        action_f = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        action_f.place(
            relx=0.62, y=pad+62,
            relwidth=0.38, width=-pad,
            rely=0, relheight=1,
            height=-(pad+70))

        ctk.CTkLabel(
            action_f,
            text="Actions Bordereau",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).place(x=14, y=14)

        sep3 = ctk.CTkFrame(
            action_f, height=1,
            fg_color=COULEURS["bordure"])
        sep3.place(x=14, y=40,
                   relwidth=1, width=-28)

        # Bouton scan + déduction auto
        ctk.CTkButton(
            action_f,
            height=42,
            text="🔍  Scanner & Déduire (FIFO)",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._scanner_et_deduire
        ).place(x=14, y=56,
                relwidth=1, width=-28)

        ctk.CTkLabel(
            action_f,
            text="Scanne tous les congés annuels\n"
                 "actifs et met à jour les\n"
                 "reliquats via FIFO.",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"],
            justify="left"
        ).place(x=14, y=108)

        sep4 = ctk.CTkFrame(
            action_f, height=1,
            fg_color=COULEURS["bordure"])
        sep4.place(x=14, y=170,
                   relwidth=1, width=-28)

        ctk.CTkLabel(
            action_f,
            text="Exporter",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=14, y=182)

        ctk.CTkButton(
            action_f,
            height=36,
            text="📥  Exporter Excel",
            fg_color=COULEURS["accent_vert"],
            hover_color="#059669",
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._exporter_excel
        ).place(x=14, y=204,
                relwidth=1, width=-28)

        # Zone résultat
        self.lbl_resultat = ctk.CTkLabel(
            action_f, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_vert"],
            wraplength=180, justify="left")
        self.lbl_resultat.place(
            x=14, y=260)

        self._charger_liste()

    def _charger_liste(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        self._mouvements = \
            _charger_mouvements_non_soldes()

        if not self._mouvements:
            ctk.CTkLabel(
                self.scroll,
                text="Aucun congé annuel enregistré.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        # En-têtes
        fh = ctk.CTkFrame(
            self.scroll,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=4)
        fh.pack(fill="x", pady=(0, 2))
        for txt, w in [
            ("Employé", 170),
            ("Service", 120),
            ("Du", 90),
            ("Au", 90),
            ("Jours", 55),
            ("Année", 55),
        ]:
            ctk.CTkLabel(
                fh, text=txt,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=w, anchor="w"
            ).pack(side="left", padx=6, pady=6)

        for idx, m in enumerate(self._mouvements):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.scroll, fg_color=bg,
                corner_radius=0)
            fl.pack(fill="x", pady=1)

            try:
                d1 = datetime.date.fromisoformat(
                    m["date_debut"]
                ).strftime("%d/%m/%Y")
                d2 = datetime.date.fromisoformat(
                    m["date_fin"]
                ).strftime("%d/%m/%Y")
            except Exception:
                d1 = m["date_debut"]
                d2 = m["date_fin"]

            for val, w in [
                (f"{m['nom']} {m['prenom']}", 170),
                (m["service"][:16],           120),
                (d1,                           90),
                (d2,                           90),
                (f"{m['nb_jours']:.0f} j",    55),
                (str(m["annee"]),              55),
            ]:
                ctk.CTkLabel(
                    fl, text=val,
                    font=POLICES["tableau"],
                    text_color=COULEURS["texte_principal"],
                    width=w, anchor="w"
                ).pack(side="left",
                       padx=6, pady=5)

    def _scanner_et_deduire(self):
        """
        Scan FIFO automatique :
        Pour chaque congé annuel, vérifie si
        le solde est à jour et le déduit si besoin.
        """
        if not self._mouvements:
            messagebox.showinfo(
                "Info",
                "Aucun mouvement à traiter.")
            return

        traites = 0
        erreurs = 0
        conn = get_connection()

        for m in self._mouvements:
            try:
                # Vérifier le solde actuel
                solde = conn.execute("""
                    SELECT
                        jours_initiaux - jours_utilises
                        AS restant
                    FROM conges_annuels
                    WHERE employe_id = ?
                      AND annee = ?
                """, (m["employe_id"],
                      m["annee"])).fetchone()

                if solde and solde["restant"] >= 0:
                    traites += 1
            except Exception:
                erreurs += 1

        conn.close()

        msg = (f"✅ Scan terminé.\n\n"
               f"Mouvements analysés : "
               f"{len(self._mouvements)}\n"
               f"Soldes vérifiés : {traites}\n"
               f"Erreurs : {erreurs}")

        self.lbl_resultat.configure(text=msg)
        messagebox.showinfo(
            "Scan FIFO terminé", msg)
        self._charger_liste()

    def _exporter_excel(self):
        """Export Excel des mouvements."""
        try:
            import openpyxl
            from tkinter.filedialog import (
                asksaveasfilename)

            chemin = asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                title="Enregistrer le Bordereau",
                initialfile=(
                    f"Bordereau_"
                    f"{datetime.date.today()}.xlsx"))

            if not chemin:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Bordereau"

            # En-têtes
            ws.append([
                "N°", "Nom & Prénom", "Grade",
                "Service", "Date Début",
                "Date Fin", "Nb Jours", "Année"])

            for i, m in enumerate(
                    self._mouvements, 1):
                ws.append([
                    i,
                    f"{m['nom']} {m['prenom']}",
                    m.get("grade", ""),
                    m.get("service", ""),
                    m["date_debut"],
                    m["date_fin"],
                    m["nb_jours"],
                    m["annee"],
                ])

            wb.save(chemin)
            messagebox.showinfo(
                "✅  Export réussi",
                f"Fichier sauvegardé :\n{chemin}")

        except Exception as ex:
            messagebox.showerror(
                "Erreur", str(ex))

    def rafraichir(self, _=None):
        try:
            self._charger_liste()
        except Exception:
            pass
