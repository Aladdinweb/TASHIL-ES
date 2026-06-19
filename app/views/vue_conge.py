# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Onglet CONGÉ — Gestion des prises de congé
Séparé de l'onglet Reliquat.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_connection
from app.utils import conges_dao
from app.views.dialogue_annulation import (
    DialogueAnnulation)


def _charger_conges_actifs() -> list:
    conn = get_connection()
    today = datetime.date.today().isoformat()
    rows = conn.execute("""
        SELECT m.id, m.type_conge,
               m.date_debut, m.date_fin,
               m.nb_jours, m.motif,
               e.id as emp_id,
               e.nom, e.prenom, e.grade,
               d.nom as service_nom,
               ca.annee
        FROM mouvements_conge m
        JOIN employes e ON e.id = m.employe_id
        JOIN departements d
            ON d.id = e.departement_id
        JOIN conges_annuels ca
            ON ca.id = m.conge_id
        WHERE m.date_fin >= ?
          AND e.actif = 1
        ORDER BY d.nom, e.nom, m.date_debut
    """, (today,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _charger_employes_par_service() -> dict:
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id, e.nom, e.prenom,
               e.grade, e.matricule,
               d.nom as service_nom
        FROM employes e
        JOIN departements d
            ON d.id = e.departement_id
        WHERE e.actif = 1
        ORDER BY d.nom, e.nom
    """).fetchall()
    conn.close()
    groupes: dict = {}
    for r in rows:
        svc = r["service_nom"]
        groupes.setdefault(svc, []).append(dict(r))
    return groupes


TYPES_LABELS = {
    "CONGE_ANNUEL":  ("📅", COULEURS["accent_bleu"]),
    "MALADIE":       ("🏥", "#EF4444"),
    "MATERNITE":     ("👶", "#8B5CF6"),
    "ARRET_TRAVAIL": ("🏥", "#EF4444"),
    "DIS_INTOX":     ("⚡", COULEURS["accent_orange"]),
    "SEMESTRE":      ("🔄", COULEURS["accent_vert"]),
}


class VueConge(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._construire()

    def _construire(self):
        pad = DIMENSIONS["padding_page"]

        # Titre + bouton demande
        ft = ctk.CTkFrame(self,
                          fg_color="transparent")
        ft.pack(fill="x", padx=pad,
                pady=(pad, 8))
        ctk.CTkLabel(
            ft, text="Gestion des Congés",
            font=POLICES["titre_page"],
            text_color=COULEURS["texte_principal"]
        ).pack(side="left")
        ctk.CTkButton(
            ft,
            text="＋  Demande de Congé",
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            text_color="#FFFFFF",
            font=POLICES["bouton"],
            height=36, width=185,
            corner_radius=DIMENSIONS["rayon_bouton"],
            command=self._ouvrir_demande
        ).pack(side="right")

        ctk.CTkFrame(
            self, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=pad, pady=(0, 10))

        # Deux panneaux
        frame_corps = ctk.CTkFrame(
            self, fg_color="transparent")
        frame_corps.pack(
            fill="both", expand=True,
            padx=pad, pady=(0, pad))
        frame_corps.grid_columnconfigure(0, weight=3)
        frame_corps.grid_columnconfigure(1, weight=2)
        frame_corps.grid_rowconfigure(0, weight=1)

        self._construire_conges_actifs(frame_corps)
        self._construire_annuaire(frame_corps)

    def _construire_conges_actifs(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        frame.grid(row=0, column=0,
                   sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(
            frame,
            text="Congés en cours & à venir",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(frame, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 8))

        self.scroll_conges = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        self.scroll_conges.pack(
            fill="both", expand=True,
            padx=14, pady=(0, 14))

        self._charger_conges()

    def _charger_conges(self):
        for w in self.scroll_conges.winfo_children():
            w.destroy()

        conges = _charger_conges_actifs()
        today  = datetime.date.today()

        if not conges:
            ctk.CTkLabel(
                self.scroll_conges,
                text="✅  Aucun congé en cours.",
                font=POLICES["corps"],
                text_color=COULEURS["accent_vert"]
            ).pack(pady=30)
            return

        for idx, c in enumerate(conges):
            bg = (COULEURS["bg_carte"]
                  if idx % 2 == 0
                  else COULEURS["bg_sidebar"])
            fm = ctk.CTkFrame(
                self.scroll_conges,
                fg_color=bg, corner_radius=6)
            fm.pack(fill="x", pady=2)

            icone, coul = TYPES_LABELS.get(
                c["type_conge"],
                ("📋", COULEURS["texte_secondaire"]))

            # Statut couleur
            try:
                d1 = datetime.date.fromisoformat(
                    c["date_debut"])
                d2 = datetime.date.fromisoformat(
                    c["date_fin"])
                if today < d1:
                    statut_coul = COULEURS["accent_orange"]
                    statut_txt  = "⏳ À venir"
                elif today == d2:
                    statut_coul = COULEURS["accent_rouge"]
                    statut_txt  = "🔔 Retour aujourd'hui"
                else:
                    statut_coul = COULEURS["accent_vert"]
                    statut_txt  = "🟢 En cours"
                d1s = d1.strftime("%d/%m/%Y")
                d2s = d2.strftime("%d/%m/%Y")
            except Exception:
                statut_coul = COULEURS["texte_discret"]
                statut_txt  = ""
                d1s = c["date_debut"]
                d2s = c["date_fin"]

            ft = ctk.CTkFrame(fm,
                              fg_color="transparent")
            ft.pack(fill="x", padx=10, pady=(6, 2))

            ctk.CTkLabel(
                ft,
                text=f"{icone} {c['nom']} "
                     f"{c['prenom']}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_principal"]
            ).pack(side="left")

            ctk.CTkLabel(
                ft, text=statut_txt,
                font=POLICES["petit"],
                text_color=statut_coul
            ).pack(side="right")

            fd = ctk.CTkFrame(fm,
                              fg_color="transparent")
            fd.pack(fill="x", padx=10, pady=(0, 4))

            ctk.CTkLabel(
                fd,
                text=f"Du {d1s} au {d2s}  "
                     f"({c['nb_jours']:.0f} j)  "
                     f"• {c['service_nom']}",
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(side="left")

            # Boutons action
            fb = ctk.CTkFrame(fm,
                              fg_color="transparent")
            fb.pack(fill="x", padx=10,
                    pady=(0, 6))

            mid = c["id"]
            ctk.CTkButton(
                fb, text="✕ Annuler/Interrompre",
                fg_color="transparent",
                hover_color=COULEURS["accent_rouge"],
                text_color=COULEURS["texte_discret"],
                font=POLICES["petit"],
                height=24, width=160,
                corner_radius=4,
                command=lambda mv=dict(c):
                    self._annuler_conge(mv)
            ).pack(side="left")

    def _construire_annuaire(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COULEURS["bg_carte"],
            corner_radius=8)
        frame.grid(row=0, column=1,
                   sticky="nsew")

        ctk.CTkLabel(
            frame,
            text="Les Services",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(padx=14, pady=(14, 4), anchor="w")
        ctk.CTkFrame(frame, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=14, pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=COULEURS["accent_bleu"])
        scroll.pack(
            fill="both", expand=True,
            padx=14, pady=(0, 14))

        groupes = _charger_employes_par_service()
        for svc, emps in groupes.items():
            # En-tête service
            fs = ctk.CTkFrame(
                scroll,
                fg_color=COULEURS["bg_sidebar"],
                corner_radius=6)
            fs.pack(fill="x", pady=(0, 2))
            ctk.CTkLabel(
                fs, text=f"  {svc}",
                font=POLICES["corps_bold"],
                text_color=COULEURS["accent_bleu"]
            ).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(
                fs, text=f"{len(emps)}",
                font=POLICES["petit"],
                text_color=COULEURS["texte_discret"]
            ).pack(side="right", padx=10)

            for idx, emp in enumerate(emps):
                bg = (COULEURS["bg_carte"]
                      if idx % 2 == 0
                      else COULEURS["bg_champ"])
                fe = ctk.CTkFrame(
                    scroll, fg_color=bg,
                    corner_radius=0,
                    cursor="hand2")
                fe.pack(fill="x", pady=1)

                ctk.CTkLabel(
                    fe,
                    text=f"{emp['nom']} "
                         f"{emp['prenom']}",
                    font=POLICES["corps"],
                    text_color=COULEURS["texte_principal"],
                    anchor="w"
                ).pack(side="left", padx=10, pady=4)

                # Clic droit → menu
                fe.bind(
                    "<Button-3>",
                    lambda e, em=emp:
                        self._menu_ctx(e, em))
                for ch in fe.winfo_children():
                    ch.bind(
                        "<Button-3>",
                        lambda e, em=emp:
                            self._menu_ctx(e, em))

    def _menu_ctx(self, event, emp):
        from app.views.dialogue_conge_rapide import (
            DialogueCongeRapide)
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        menu.configure(
            fg_color=COULEURS["bg_carte"])
        menu.geometry(
            f"220x140+{event.x_root}"
            f"+{event.y_root}")

        ctk.CTkLabel(
            menu,
            text=f"{emp['nom']} {emp['prenom']}"[:22],
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"]
        ).pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkFrame(
            menu, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=8)

        for lbl, tp in [
            ("📅  Congé Annuel",  "CONGE_ANNUEL"),
            ("🏥  Congé Maladie", "MALADIE"),
            ("👶  Maternité",     "MATERNITE"),
        ]:
            def _cmd(t=tp, m=menu, e=emp):
                m.destroy()
                DialogueCongeRapide(
                    self, emp=e, type_conge=t,
                    callback=self.rafraichir)
            ctk.CTkButton(
                menu, text=lbl,
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                font=POLICES["corps"],
                height=30, anchor="w",
                corner_radius=0,
                command=_cmd
            ).pack(fill="x", padx=4, pady=1)

        menu.bind("<FocusOut>",
                  lambda e: menu.destroy())
        menu.focus_set()

    def _ouvrir_demande(self):
        from app.views.dialogue_conge_rapide import (
            DialogueCongeRapide)
        # Sélection employé puis type
        from app.utils.conges_dao import (
            lister_employes_actifs)
        emps = lister_employes_actifs()
        if not emps:
            from tkinter import messagebox
            messagebox.showwarning(
                "Aucun employé",
                "Ajoutez d'abord des employés.")
            return
        emp = emps[0]
        DialogueCongeRapide(
            self, emp=emp,
            type_conge="CONGE_ANNUEL",
            callback=self.rafraichir)

    def _annuler_conge(self, mouvement):
        DialogueAnnulation(
            self, mouvement=mouvement,
            callback_succes=self.rafraichir)

    def rafraichir(self, _=None):
        try:
            self._charger_conges()
        except Exception:
            pass
