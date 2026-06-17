# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Fiche individuelle employé — EPSP ES-SENIA
Historique complet de tous les mouvements administratifs.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection


def _charger_fiche(emp_id: int) -> dict:
    conn = get_connection()

    emp = conn.execute("""
        SELECT e.*, d.code as dept_code, d.nom as dept_nom,
               p.nom as poly_nom
        FROM employes e
        JOIN departements d ON d.id = e.departement_id
        LEFT JOIN polycliniques p ON p.id = e.polyclinique_id
        WHERE e.id = ?
    """, (emp_id,)).fetchone()

    soldes = conn.execute("""
        SELECT annee, jours_initiaux, jours_utilises,
               (jours_initiaux - jours_utilises) as restant,
               est_reporte
        FROM conges_annuels
        WHERE employe_id = ?
        ORDER BY annee ASC
    """, (emp_id,)).fetchall()

    mouvements = conn.execute("""
        SELECT m.type_conge, m.date_debut, m.date_fin,
               m.nb_jours, m.observation, m.created_at,
               ca.annee
        FROM mouvements_conge m
        JOIN conges_annuels ca ON ca.id = m.conge_id
        WHERE m.employe_id = ?
        ORDER BY m.date_debut DESC
    """, (emp_id,)).fetchall()

    conn.close()
    return {
        "employe":    dict(emp) if emp else {},
        "soldes":     [dict(s) for s in soldes],
        "mouvements": [dict(m) for m in mouvements],
    }


TYPES_LABELS = {
    "CONGE_ANNUEL":  ("📅", "Congé Annuel",
                      "#3B82F6"),
    "DIS_INTOX":     ("⚡", "Dis-Intox Radiation",
                      "#F59E0B"),
    "SEMESTRE":      ("🔄", "Semestre Radiation",
                      "#10B981"),
    "ARRET_TRAVAIL": ("🏥", "Arrêt de Travail",
                      "#EF4444"),
    "REPRISE":       ("✅", "Reprise de Travail",
                      "#10B981"),
    "NAISSANCE":     ("👶", "Congé Naissance",
                      "#8B5CF6"),
    "ANNULATION":    ("❌", "Annulation",
                      "#6B7280"),
    "ROLLOVER":      ("🔁", "Rollover 1er Mai",
                      "#F59E0B"),
}


class FicheEmploye(ctk.CTkToplevel):
    def __init__(self, parent, emp_id: int):
        super().__init__(parent)
        self._emp_id = emp_id
        self.configure(fg_color=COULEURS["bg_principal"])
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()

        self.update_idletasks()
        w, h = 860, 680
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(700, 500)

        fiche = _charger_fiche(emp_id)
        self.title(
            f"Fiche — {fiche['employe'].get('nom','')} "
            f"{fiche['employe'].get('prenom','')}")
        self._construire(fiche)

    def _construire(self, fiche: dict):
        emp = fiche["employe"]
        pad = 20

        # ── En-tête ───────────────────────────────────────────
        frame_head = ctk.CTkFrame(
            self, fg_color=COULEURS["bg_sidebar"],
            corner_radius=0, height=100)
        frame_head.pack(fill="x")
        frame_head.pack_propagate(False)

        # Badge initiales
        initiales = (emp.get("nom", "?")[:1] +
                     emp.get("prenom", "?")[:1])
        badge = ctk.CTkFrame(
            frame_head,
            fg_color=COULEURS["accent_bleu"],
            corner_radius=30, width=60, height=60)
        badge.place(x=20, y=20)
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text=initiales,
            font=("Segoe UI", 20, "bold"),
            text_color="#FFFFFF").place(
                relx=0.5, rely=0.5, anchor="center")

        # Infos principales
        ctk.CTkLabel(
            frame_head,
            text=f"{emp.get('nom','')} {emp.get('prenom','')}",
            font=("Segoe UI", 18, "bold"),
            text_color=COULEURS["texte_principal"]
        ).place(x=96, y=18)

        ctk.CTkLabel(
            frame_head,
            text=f"{emp.get('grade','')}  •  "
                 f"{emp.get('dept_code','')}  •  "
                 f"Mat. {emp.get('matricule','')}",
            font=POLICES["corps"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=96, y=46)

        poly = emp.get("poly_nom", "") or "—"
        annee_entree = emp.get("annee_entree", "")
        ctk.CTkLabel(
            frame_head,
            text=f"🏥 {poly}  "
                 f"{'  •  Entrée : ' + str(annee_entree) if annee_entree else ''}",
            font=POLICES["petit"],
            text_color=COULEURS["texte_discret"]
        ).place(x=96, y=70)

        # Statut badge
        statut = "● Actif" if emp.get("actif") else "● Inactif"
        coul_s = (COULEURS["accent_vert"]
                  if emp.get("actif")
                  else COULEURS["accent_rouge"])
        ctk.CTkLabel(
            frame_head, text=statut,
            font=POLICES["corps_bold"],
            text_color=coul_s
        ).place(relx=0.98, rely=0.3, anchor="e")

        # ── Corps : 2 colonnes ────────────────────────────────
        frame_corps = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_corps.pack(
            fill="both", expand=True, padx=pad, pady=pad)
        frame_corps.grid_columnconfigure(0, weight=2)
        frame_corps.grid_columnconfigure(1, weight=3)
        frame_corps.grid_rowconfigure(0, weight=1)

        # Colonne gauche : soldes
        self._construire_soldes(
            frame_corps, fiche["soldes"])

        # Colonne droite : historique mouvements
        self._construire_historique(
            frame_corps, fiche["mouvements"])

        # Bouton fermer
        ctk.CTkButton(
            self, text="Fermer",
            fg_color=COULEURS["bg_champ"],
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["bouton"],
            height=36, width=120,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self.destroy
        ).pack(pady=(0, pad))

    def _construire_soldes(self, parent, soldes):
        frame = ctk.CTkFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        frame.grid(row=0, column=0, sticky="nsew",
                   padx=(0, 8))

        ctk.CTkLabel(
            frame, text="Soldes par année",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(frame, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 10))

        if not soldes:
            ctk.CTkLabel(
                frame, text="Aucun solde enregistré.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=20)
            return

        annee_courante = datetime.date.today().year

        for s in soldes:
            restant = s["restant"]
            annee   = s["annee"]
            is_old  = annee < annee_courante

            bg_card = (COULEURS["bg_sidebar"]
                       if is_old else COULEURS["bg_champ"])
            coul_r  = (COULEURS["accent_vert"]
                       if restant > 10
                       else COULEURS["accent_orange"]
                       if restant > 0
                       else COULEURS["accent_rouge"])

            f = ctk.CTkFrame(frame, fg_color=bg_card,
                             corner_radius=6)
            f.pack(fill="x", padx=14, pady=3)

            f_top = ctk.CTkFrame(f, fg_color="transparent")
            f_top.pack(fill="x", padx=10, pady=(6, 2))

            tag = " 🔴 RELIQUAT" if is_old else " ✅ EN COURS"
            ctk.CTkLabel(
                f_top,
                text=f"Année {annee}{tag}",
                font=POLICES["corps_bold"],
                text_color=(COULEURS["accent_orange"]
                            if is_old
                            else COULEURS["accent_vert"])
            ).pack(side="left")

            if s.get("est_reporte"):
                ctk.CTkLabel(
                    f_top, text="[clôturé]",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"]
                ).pack(side="right")

            f_det = ctk.CTkFrame(f, fg_color="transparent")
            f_det.pack(fill="x", padx=10, pady=(0, 6))

            for label, val in [
                ("Initiaux",  f"{s['jours_initiaux']:.0f} j"),
                ("Utilisés",  f"{s['jours_utilises']:.0f} j"),
                ("Restants",  f"{restant:.0f} j"),
            ]:
                fc = ctk.CTkFrame(f_det,
                                  fg_color="transparent")
                fc.pack(side="left", padx=(0, 12))
                ctk.CTkLabel(
                    fc, text=label,
                    font=POLICES["stat_label"],
                    text_color=COULEURS["texte_discret"]
                ).pack()
                ctk.CTkLabel(
                    fc, text=val,
                    font=POLICES["corps_bold"],
                    text_color=(coul_r
                                if label == "Restants"
                                else COULEURS["texte_principal"])
                ).pack()

    def _construire_historique(self, parent, mouvements):
        frame = ctk.CTkFrame(
            parent, fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        frame.grid(row=0, column=1, sticky="nsew")

        f_titre = ctk.CTkFrame(frame, fg_color="transparent")
        f_titre.pack(fill="x", padx=14, pady=(14, 4))
        ctk.CTkLabel(
            f_titre,
            text="Historique des mouvements",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        ctk.CTkLabel(
            f_titre,
            text=f"{len(mouvements)} entrée(s)",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(side="right")

        ctk.CTkFrame(frame, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(
            frame, fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(fill="both", expand=True,
                    padx=14, pady=(0, 14))

        if not mouvements:
            ctk.CTkLabel(
                scroll,
                text="Aucun mouvement enregistré.",
                font=POLICES["corps"],
                text_color=COULEURS["texte_discret"]
            ).pack(pady=30)
            return

        for idx, m in enumerate(mouvements):
            icone, libelle, coul = TYPES_LABELS.get(
                m["type_conge"],
                ("📋", m["type_conge"], "#94A3B8"))

            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_sidebar"])
            f = ctk.CTkFrame(scroll, fg_color=bg,
                             corner_radius=6)
            f.pack(fill="x", pady=2)

            f_top = ctk.CTkFrame(f, fg_color="transparent")
            f_top.pack(fill="x", padx=10, pady=(6, 2))

            # Icône + type
            ctk.CTkLabel(
                f_top, text=f"{icone} {libelle}",
                font=POLICES["corps_bold"],
                text_color=coul
            ).pack(side="left")

            # Jours
            ctk.CTkLabel(
                f_top,
                text=f"{m['nb_jours']:.0f} j",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="right")

            # Dates
            try:
                d1 = datetime.date.fromisoformat(
                    m["date_debut"]).strftime("%d/%m/%Y")
                d2 = datetime.date.fromisoformat(
                    m["date_fin"]).strftime("%d/%m/%Y")
                dates_txt = f"Du {d1} au {d2}"
            except Exception:
                dates_txt = (f"{m['date_debut']} → "
                             f"{m['date_fin']}")

            f_det = ctk.CTkFrame(f, fg_color="transparent")
            f_det.pack(fill="x", padx=10, pady=(0, 6))

            ctk.CTkLabel(
                f_det, text=dates_txt,
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(side="left")

            if m.get("observation"):
                ctk.CTkLabel(
                    f_det,
                    text=f"— {m['observation'][:40]}",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_discret"]
                ).pack(side="left", padx=(8, 0))

            ctk.CTkLabel(
                f_det,
                text=f"Exo. {m['annee']}",
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(side="right")
