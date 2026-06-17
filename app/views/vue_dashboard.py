# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Vue : Tableau de bord — EPSP ES-SENIA
Compteurs live, reliquats critiques, employés en congé cliquables.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection


def _stats() -> dict:
    conn = get_connection()
    c    = conn.cursor()
    aujourd_hui = datetime.date.today().isoformat()
    annee       = datetime.date.today().year

    total_emp  = c.execute(
        "SELECT COUNT(*) FROM employes WHERE actif=1"
    ).fetchone()[0]

    total_dept = c.execute(
        "SELECT COUNT(*) FROM departements"
    ).fetchone()[0]

    row = c.execute("""
        SELECT
            SUM(jours_initiaux - jours_utilises) as restants,
            SUM(jours_utilises) as utilises
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        WHERE ca.annee = ? AND e.actif = 1
    """, (annee,)).fetchone()
    restants = row[0] or 0
    utilises = row[1] or 0

    # Employés actuellement en congé
    en_conge = c.execute("""
        SELECT DISTINCT e.id, e.nom, e.prenom,
               e.grade, d.code as dept_code,
               m.date_debut, m.date_fin, m.nb_jours
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
        JOIN departements d ON d.id = e.departement_id
        WHERE m.date_debut <= ? AND m.date_fin >= ?
          AND e.actif = 1
        ORDER BY m.date_fin ASC
    """, (aujourd_hui, aujourd_hui)).fetchall()

    reliquats = c.execute("""
        SELECT e.nom, e.prenom, e.grade, ca.annee,
               (ca.jours_initiaux - ca.jours_utilises) as restant
        FROM conges_annuels ca
        JOIN employes e ON e.id = ca.employe_id
        WHERE (ca.jours_initiaux - ca.jours_utilises) > 0
          AND ca.annee < ?
          AND e.actif = 1
        ORDER BY restant DESC
        LIMIT 10
    """, (annee,)).fetchall()

    conn.close()
    return {
        "total_emp":  total_emp,
        "total_dept": total_dept,
        "restants":   restants,
        "utilises":   utilises,
        "en_conge":   [dict(r) for r in en_conge],
        "reliquats":  [dict(r) for r in reliquats],
    }


class VueDashboard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         fg_color=COULEURS["bg_principal"],
                         corner_radius=0, **kwargs)
        self._timer_id = None
        self._construire()
        self._demarrer_rafraichissement()

    def _construire(self):
        stats = _stats()
        pad   = DIMENSIONS["padding_page"]

        # Titre
        frame_titre = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_titre.pack(fill="x", padx=pad,
                         pady=(pad, 8))
        ctk.CTkLabel(
            frame_titre, text="Tableau de bord",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        today = datetime.date.today().strftime("%d/%m/%Y")
        ctk.CTkLabel(
            frame_titre, text=f"EPSP ES-SENIA  •  {today}",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(side="right")

        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, pad))

        # ── Cartes statistiques ───────────────────────────────
        frame_cartes = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_cartes.pack(fill="x", padx=pad,
                          pady=(0, pad))

        nb_conge = len(stats["en_conge"])

        cartes = [
            ("EMPLOYÉS ACTIFS",
             str(stats["total_emp"]),
             "Tous services",
             COULEURS["accent_bleu"], None),
            ("DÉPARTEMENTS",
             str(stats["total_dept"]),
             "Unités admin",
             COULEURS["accent_vert"], None),
            ("EN CONGÉ AUJOURD'HUI",
             str(nb_conge),
             "Cliquer pour la liste",
             COULEURS["accent_orange"],
             lambda s=stats: self._popup_en_conge(s["en_conge"])),
            ("JOURS RESTANTS",
             f"{stats['restants']:.0f} j",
             f"Exercice {datetime.date.today().year}",
             COULEURS["accent_rouge"], None),
        ]

        for i, (titre, val, sous, coul, cmd) in enumerate(cartes):
            frame_cartes.columnconfigure(i, weight=1)
            carte = self._carte_stat(
                frame_cartes, titre, val, sous, coul, cmd)
            carte.grid(row=0, column=i,
                       padx=6, pady=0, sticky="nsew")

        # ── Reliquats critiques ───────────────────────────────
        ctk.CTkFrame(self, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=pad, pady=(0, 14))

        ctk.CTkLabel(
            self,
            text="⚠  Reliquats années antérieures non soldés",
            font=POLICES["sous_titre"],
            text_color=COULEURS["accent_orange"]
        ).pack(anchor="w", padx=pad, pady=(0, 8))

        cols = [
            ("Nom & Prénom",   200),
            ("Grade",          180),
            ("Année",           70),
            ("Jours restants", 120),
        ]

        # En-têtes
        frame_head = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=6)
        frame_head.pack(fill="x", padx=pad, pady=(0, 2))
        for nom, larg in cols:
            ctk.CTkLabel(
                frame_head, text=nom,
                font=POLICES["tableau_head"],
                text_color=COULEURS["texte_secondaire"],
                width=larg, anchor="w"
            ).pack(side="left", padx=8, pady=6)

        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(fill="both", expand=True,
                    padx=pad, pady=(0, pad))

        if stats["reliquats"]:
            for idx, r in enumerate(stats["reliquats"]):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_champ"])
                f = ctk.CTkFrame(scroll, fg_color=bg,
                                 corner_radius=0)
                f.pack(fill="x", pady=1)
                coul_j = (COULEURS["accent_rouge"]
                          if r["restant"] > 15
                          else COULEURS["accent_orange"])
                for val, (_, larg) in zip(
                    [f"{r['nom']} {r['prenom']}",
                     r["grade"],
                     str(r["annee"]),
                     f"{r['restant']:.0f} j"],
                    cols
                ):
                    ctk.CTkLabel(
                        f, text=val,
                        font=POLICES["tableau"],
                        text_color=COULEURS["texte_principal"],
                        width=larg, anchor="w"
                    ).pack(side="left", padx=8, pady=5)
        else:
            ctk.CTkLabel(
                scroll,
                text="✓  Aucun reliquat non soldé — situation nette.",
                font=POLICES["corps"],
                text_color=COULEURS["accent_vert"]
            ).pack(pady=20)

    def _carte_stat(self, parent, titre, valeur, sous,
                    couleur, commande=None):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=DIMENSIONS["rayon_carte"],
            border_width=1,
            border_color=couleur,
            cursor="hand2" if commande else "arrow")

        # Bande colorée
        ctk.CTkFrame(frame, height=4,
                     fg_color=couleur,
                     corner_radius=0).pack(
                         fill="x", side="top")

        corps = ctk.CTkFrame(frame,
                             fg_color="transparent")
        corps.pack(fill="both", expand=True,
                   padx=14, pady=12)

        ctk.CTkLabel(
            corps, text=titre,
            font=POLICES["stat_label"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            corps, text=valeur,
            font=POLICES["stat_chiffre"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w", pady=(2, 0))

        if sous:
            ctk.CTkLabel(
                corps, text=sous,
                font=POLICES["petit"],
                text_color=(COULEURS["accent_bleu"]
                            if commande
                            else COULEURS["texte_discret"])
            ).pack(anchor="w")

        if commande:
            frame.bind("<Button-1>",
                       lambda e: commande())
            for child in frame.winfo_children():
                child.bind("<Button-1>",
                           lambda e: commande())
        return frame

    def _popup_en_conge(self, en_conge: list):
        """Popup liste des employés actuellement en congé."""
        popup = ctk.CTkToplevel(self)
        popup.title("Employés en congé aujourd'hui")
        popup.configure(fg_color=COULEURS["bg_principal"])
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_set()

        w, h = 600, 420
        popup.update_idletasks()
        x = (popup.winfo_screenwidth()  - w) // 2
        y = (popup.winfo_screenheight() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        today = datetime.date.today().strftime("%d/%m/%Y")
        ctk.CTkLabel(
            popup,
            text=f"🏖  Employés en congé — {today}",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=20, pady=(16, 8), anchor="w")

        ctk.CTkFrame(popup, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=20, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(
            popup, fg_color=COULEURS["bg_carte"],
            corner_radius=8,
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(fill="both", expand=True,
                    padx=20, pady=(0, 10))

        if not en_conge:
            ctk.CTkLabel(
                scroll,
                text="Aucun employé en congé aujourd'hui.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
        else:
            for idx, emp in enumerate(en_conge):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_sidebar"])
                f = ctk.CTkFrame(scroll, fg_color=bg,
                                 corner_radius=6)
                f.pack(fill="x", pady=2)

                f_top = ctk.CTkFrame(
                    f, fg_color="transparent")
                f_top.pack(fill="x", padx=10,
                           pady=(6, 2))

                ctk.CTkLabel(
                    f_top,
                    text=(f"👤 {emp['nom']} "
                          f"{emp['prenom']}"),
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["texte_principal"]
                ).pack(side="left")

                ctk.CTkLabel(
                    f_top,
                    text=f"{emp['nb_jours']:.0f} j",
                    font=POLICES["corps_bold"],
                    text_color=COULEURS["accent_bleu"]
                ).pack(side="right")

                f_det = ctk.CTkFrame(
                    f, fg_color="transparent")
                f_det.pack(fill="x", padx=10,
                           pady=(0, 6))

                try:
                    d1 = datetime.date.fromisoformat(
                        emp["date_debut"]
                    ).strftime("%d/%m/%Y")
                    d2 = datetime.date.fromisoformat(
                        emp["date_fin"]
                    ).strftime("%d/%m/%Y")
                    date_txt = f"Du {d1} au {d2}"
                except Exception:
                    date_txt = ""

                ctk.CTkLabel(
                    f_det, text=date_txt,
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(side="left")

                ctk.CTkLabel(
                    f_det,
                    text=emp.get("dept_code", ""),
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"]
                ).pack(side="right")

        ctk.CTkButton(
            popup, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=34, width=100,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=popup.destroy
        ).pack(pady=(0, 16))

    def _demarrer_rafraichissement(self):
        """Rafraîchit le dashboard toutes les 60 secondes."""
        self._timer_id = self.after(60000, self._auto_refresh)

    def _auto_refresh(self):
        self.rafraichir()

    def rafraichir(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        for w in self.winfo_children():
            w.destroy()
        self._construire()
        self._demarrer_rafraichissement()
