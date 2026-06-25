# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Tableau de Service — Grille éditable mensuelle
Verrouillage auto des cellules congé.
"""
import datetime
import calendar
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection

try:
    from app.config import TYPES_SERVICE
except Exception:
    TYPES_SERVICE = [
        "Matin", "Soir", "Nuit",
        "Garde", "Repos", "Congé", "Absent"]


def _charger_employes_service(service: str) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id, e.nom, e.prenom, e.grade
        FROM employes e
        JOIN departements d
            ON d.id = e.departement_id
        WHERE d.nom = ? AND e.actif = 1
        ORDER BY e.nom
    """, (service,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _jours_en_conge(emp_id: int,
                    annee: int,
                    mois: int) -> set:
    """Retourne les jours où l'employé est en congé."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT date_debut, date_fin
        FROM mouvements_conge
        WHERE employe_id = ?
          AND type_conge = 'CONGE_ANNUEL'
          AND strftime('%Y', date_debut) <= ?
          AND strftime('%Y', date_fin)   >= ?
    """, (emp_id, str(annee), str(annee))
    ).fetchall()
    conn.close()

    jours_conge = set()
    for r in rows:
        try:
            d1 = datetime.date.fromisoformat(
                r["date_debut"])
            d2 = datetime.date.fromisoformat(
                r["date_fin"])
            d  = d1
            while d <= d2:
                if d.year == annee and d.month == mois:
                    jours_conge.add(d.day)
                d += datetime.timedelta(days=1)
        except Exception:
            pass
    return jours_conge


class VueTableauService(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        today = datetime.date.today()
        self._annee  = today.year
        self._mois   = today.month
        self._service = "Urgences"
        self._cellules = {}  # (emp_id, jour) → widget
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Barre de contrôle
        ctrl = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        ctrl.place(x=pad, y=pad,
                   relwidth=1, width=-pad*2,
                   height=60)

        # Sélecteur mois
        ctk.CTkLabel(
            ctrl, text="Mois :",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=14, y=18)

        mois_list = [
            f"{m:02d} — {calendar.month_name[m]}"
            for m in range(1, 13)]
        self.m_mois = ctk.CTkOptionMenu(
            ctrl, values=mois_list,
            width=160, height=30,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=6,
            command=self._on_mois_change)
        self.m_mois.place(x=60, y=16)
        self.m_mois.set(
            f"{self._mois:02d} — "
            f"{calendar.month_name[self._mois]}")

        # Sélecteur service
        ctk.CTkLabel(
            ctrl, text="Service :",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=234, y=18)

        try:
            from app.config import SERVICES_CLINIQUES
            svcs = SERVICES_CLINIQUES
        except Exception:
            svcs = ["Urgences", "Consultation",
                    "Pharmacie", "Autre"]

        self.m_svc = ctk.CTkOptionMenu(
            ctrl, values=svcs,
            width=200, height=30,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=6,
            command=self._on_svc_change)
        self.m_svc.place(x=296, y=16)
        self.m_svc.set(self._service)

        # Bouton sauvegarder
        ctk.CTkButton(
            ctrl, text="💾  Sauvegarder",
            width=130, height=30,
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            corner_radius=6,
            command=self._sauvegarder
        ).place(relx=1.0, x=-154, y=16)

        # Bouton importer gabarit
        ctk.CTkButton(
            ctrl, text="📂  Importer gabarit",
            width=140, height=30,
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            corner_radius=6,
            command=self._importer_gabarit
        ).place(relx=1.0, x=-302, y=16)

        # Zone grille
        self.frame_grille = ctk.CTkScrollableFrame(
            self,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.frame_grille.place(
            x=pad, y=pad+70,
            relwidth=1, width=-pad*2,
            relheight=1, height=-(pad+80))

        self._generer_grille()

    def _on_mois_change(self, val: str):
        try:
            self._mois = int(val.split("—")[0].strip())
        except Exception:
            pass
        self._generer_grille()

    def _on_svc_change(self, val: str):
        self._service = val
        self._generer_grille()

    def _generer_grille(self):
        for w in self.frame_grille.winfo_children():
            w.destroy()
        self._cellules = {}

        employes = _charger_employes_service(
            self._service)

        nb_jours = calendar.monthrange(
            self._annee, self._mois)[1]
        jours = list(range(1, nb_jours + 1))

        # Couleurs jours de semaine
        def couleur_jour(j: int) -> str:
            d = datetime.date(
                self._annee, self._mois, j)
            if d.weekday() >= 5:  # Weekend
                return COULEURS["accent_orange"]
            return COULEURS["texte_secondaire"]

        # En-tête — jours du mois
        fh = ctk.CTkFrame(
            self.frame_grille,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=4)
        fh.pack(fill="x", pady=(0, 2))

        # Colonne nom
        ctk.CTkLabel(
            fh, text="Employé",
            font=POLICES["tableau_head"],
            text_color=COULEURS["texte_secondaire"],
            width=160, anchor="w"
        ).pack(side="left", padx=6, pady=6)

        for j in jours:
            ctk.CTkLabel(
                fh, text=str(j),
                font=("Segoe UI", 9, "bold"),
                text_color=couleur_jour(j),
                width=32, anchor="center"
            ).pack(side="left", padx=1)

        if not employes:
            ctk.CTkLabel(
                self.frame_grille,
                text=f"Aucun employé dans "
                     f"« {self._service} ».",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        # Lignes employés
        for idx, emp in enumerate(employes):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_champ"])
            fl = ctk.CTkFrame(
                self.frame_grille,
                fg_color=bg, corner_radius=0)
            fl.pack(fill="x", pady=1)

            # Nom
            ctk.CTkLabel(
                fl,
                text=f"{emp['nom']} "
                     f"{emp['prenom']}"[:20],
                font=POLICES["tableau"],
                text_color=COULEURS["texte_principal"],
                width=160, anchor="w"
            ).pack(side="left", padx=6, pady=4)

            # Jours en congé
            jours_conge = _jours_en_conge(
                emp["id"],
                self._annee, self._mois)

            for j in jours:
                est_conge = j in jours_conge

                if est_conge:
                    # Cellule verrouillée
                    lbl = ctk.CTkLabel(
                        fl, text="C",
                        font=("Segoe UI", 8, "bold"),
                        text_color="#FFFFFF",
                        fg_color=COULEURS["accent_orange"],
                        corner_radius=3,
                        width=30, height=22)
                    lbl.pack(
                        side="left", padx=1, pady=2)
                else:
                    # Cellule éditable
                    var = ctk.StringVar(value="")

                    # Charger valeur sauvegardée
                    val_db = self._charger_cellule(
                        emp["id"], j)
                    if val_db:
                        var.set(val_db[:1].upper())

                    entry = ctk.CTkEntry(
                        fl, textvariable=var,
                        width=30, height=22,
                        fg_color=COULEURS["bg_champ"],
                        border_color=COULEURS["bordure"],
                        text_color=COULEURS["texte_principal"],
                        font=("Segoe UI", 8),
                        justify="center",
                        corner_radius=3)
                    entry.pack(
                        side="left", padx=1, pady=2)
                    self._cellules[
                        (emp["id"], j)] = var

    def _charger_cellule(
            self, emp_id: int, jour: int) -> str:
        try:
            conn = get_connection()
            row = conn.execute("""
                SELECT type_service
                FROM tableau_service
                WHERE employe_id=?
                  AND annee=? AND mois=? AND jour=?
            """, (emp_id, self._annee,
                  self._mois, jour)).fetchone()
            conn.close()
            return row["type_service"] if row else ""
        except Exception:
            return ""

    def _sauvegarder(self):
        conn = get_connection()
        count = 0
        for (emp_id, jour), var in \
                self._cellules.items():
            val = var.get().strip()
            if not val:
                continue
            # Normaliser
            val_norm = val.upper()
            try:
                conn.execute("""
                    INSERT INTO tableau_service
                        (employe_id, annee, mois,
                         jour, type_service)
                    VALUES (?,?,?,?,?)
                    ON CONFLICT(employe_id,
                        annee, mois, jour)
                    DO UPDATE SET
                        type_service=excluded.type_service
                """, (emp_id, self._annee,
                      self._mois, jour, val_norm))
                count += 1
            except Exception:
                pass
        conn.commit()
        conn.close()
        messagebox.showinfo(
            "✅  Sauvegardé",
            f"{count} cellule(s) enregistrée(s).")

    def _importer_gabarit(self):
        chemin = filedialog.askopenfilename(
            title="Importer un gabarit",
            filetypes=[
                ("Excel", "*.xlsx *.xls"),
                ("Tous", "*.*"),
            ])
        if chemin:
            messagebox.showinfo(
                "Gabarit importé",
                f"Fichier sélectionné :\n"
                f"{chemin}\n\n"
                "Intégration en cours de développement.")

    def rafraichir(self, _=None):
        try:
            self._generer_grille()
        except Exception:
            pass
