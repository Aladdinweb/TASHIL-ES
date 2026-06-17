# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Fenêtre principale — EPSP ES-SENIA"""
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import faire_backup
from app.views.vue_dashboard import VueDashboard
from app.views.vue_employes import VueEmployes
from app.views.vue_conges import VueConges
from app.views.vue_bordereaux import VueBordereaux
from app.views.vue_rollover import VueRollover

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FenetrePrincipale(ctk.CTk):
    ONGLETS = [
        ("dashboard",  "Tableau de bord",   "◉"),
        ("employes",   "Employés",           "👤"),
        ("conges",     "Congés & Reliquats", "📅"),
        ("bordereaux", "Bordereaux",         "📄"),
        ("admin",      "Administration",     "⚙"),
    ]

    def __init__(self):
        super().__init__()
        self._vue_active  = ""
        self._boutons_nav = {}
        self._vues_cache  = {}
        self._configurer_fenetre()
        self._construire_layout()
        self._verifier_rollover_auto()
        self._naviguer("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._fermeture)

    def _configurer_fenetre(self):
        self.title(
            "EPSP ES-SENIA — Gestionnaire de Congés Annuels")
        w = DIMENSIONS["fenetre_w"]
        h = DIMENSIONS["fenetre_h"]
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(DIMENSIONS["fenetre_min_w"],
                     DIMENSIONS["fenetre_min_h"])
        self.configure(fg_color=COULEURS["bg_principal"])

    def _construire_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._construire_sidebar()
        self._construire_zone_contenu()

    def _construire_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=DIMENSIONS["sidebar_w"],
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        frame_logo = ctk.CTkFrame(
            sidebar, fg_color="transparent")
        frame_logo.pack(fill="x", padx=16,
                        pady=(24, 0))
        badge = ctk.CTkFrame(
            frame_logo,
            fg_color=COULEURS["accent_bleu"],
            corner_radius=8, width=44, height=44)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text="ES",
            font=("Segoe UI", 16, "bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5, anchor="center")

        f_txt = ctk.CTkFrame(frame_logo,
                             fg_color="transparent")
        f_txt.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            f_txt, text="EPSP",
            font=POLICES["titre_app"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            f_txt, text="ES-SENIA",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=16,
                         pady=(20, 16))
        ctk.CTkLabel(
            sidebar, text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=COULEURS["texte_discret"]
        ).pack(anchor="w", padx=20, pady=(0, 8))

        for cle, libelle, icone in self.ONGLETS:
            if cle == "admin":
                ctk.CTkFrame(
                    sidebar, height=1,
                    fg_color=COULEURS["bordure"]
                ).pack(fill="x", padx=16,
                       pady=(8, 8))
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icone}   {libelle}",
                anchor="w",
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["sidebar_inact_txt"],
                font=POLICES["nav"], height=42,
                corner_radius=8,
                command=lambda c=cle: self._naviguer(c))
            btn.pack(fill="x", padx=12, pady=2)
            self._boutons_nav[cle] = btn

        # Pied sidebar — Vérifier MAJ + copyright
        frame_pied = ctk.CTkFrame(
            sidebar, fg_color="transparent")
        frame_pied.pack(side="bottom", fill="x",
                        padx=16, pady=20)

        ctk.CTkFrame(frame_pied, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", pady=(0, 10))

        ctk.CTkButton(
            frame_pied,
            text="🔄  Vérifier les mises à jour",
            fg_color="transparent",
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_discret"],
            font=("Segoe UI", 9),
            height=28,
            corner_radius=6,
            command=self._verifier_maj
        ).pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            frame_pied,
            text="COPYRIGHT\nILINE TECH 2026\nBY FERAK ALADDIN",
            font=("Segoe UI", 8),
            text_color=COULEURS["texte_discret"],
            justify="center"
        ).pack()

    def _construire_zone_contenu(self):
        self.frame_contenu = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0)
        self.frame_contenu.grid(
            row=0, column=1, sticky="nsew")
        self.frame_contenu.grid_rowconfigure(0, weight=1)
        self.frame_contenu.grid_columnconfigure(0, weight=1)

    def _naviguer(self, cle: str):
        if cle == self._vue_active:
            return
        for k, btn in self._boutons_nav.items():
            if k == cle:
                btn.configure(
                    fg_color=COULEURS["sidebar_active_bg"],
                    text_color=COULEURS["sidebar_active_txt"])
            else:
                if k != "admin" or "⚠" not in btn.cget("text"):
                    btn.configure(
                        fg_color="transparent",
                        text_color=COULEURS["sidebar_inact_txt"])
        if (self._vue_active and
                self._vue_active in self._vues_cache):
            self._vues_cache[self._vue_active].grid_remove()
        if cle not in self._vues_cache:
            vue = self._creer_vue(cle)
            vue.grid(row=0, column=0, sticky="nsew")
            self._vues_cache[cle] = vue
        else:
            self._vues_cache[cle].grid()
            self._vues_cache[cle].rafraichir()
        self._vue_active = cle

    def _creer_vue(self, cle: str):
        vues = {
            "dashboard":  VueDashboard,
            "employes":   VueEmployes,
            "conges":     VueConges,
            "bordereaux": VueBordereaux,
            "admin":      VueRollover,
        }
        cls = vues.get(cle)
        if not cls:
            raise ValueError(f"Vue inconnue : {cle}")
        return cls(self.frame_contenu)

    def _verifier_rollover_auto(self):
        from app.utils.deduction_engine import (
            verifier_rollover_necessaire)
        if verifier_rollover_necessaire():
            btn = self._boutons_nav.get("admin")
            if btn:
                btn.configure(
                    text="  ⚙   Administration ⚠",
                    text_color=COULEURS["accent_orange"])

    # ── Vérification MAJ ──────────────────────────────────
    def _verifier_maj(self):
        from app.utils.updater import (
            verifier_en_arriere_plan,
            version_plus_recente)

        btn = self._boutons_nav.get("admin")

        def _callback(info):
            if info is None:
                self.after(0, lambda: messagebox.showinfo(
                    "Mise à jour",
                    "Impossible de vérifier (pas de connexion)."))
                return

            tag = info.get("tag", "")
            if version_plus_recente(tag):
                self.after(0, lambda: self._proposer_maj(info))
            else:
                self.after(0, lambda: messagebox.showinfo(
                    "Mise à jour",
                    f"✅ Vous utilisez la dernière version.\n"
                    f"Version distante : {tag}"))

        verifier_en_arriere_plan(_callback)

    def _proposer_maj(self, info: dict):
        import sys
        from app.utils.updater import telecharger_et_remplacer

        rep = messagebox.askyesno(
            "Nouvelle version disponible",
            f"Version {info['tag']} disponible !\n\n"
            f"{info.get('notes','')}\n\n"
            f"Taille : "
            f"{info.get('taille',0) // 1024 // 1024} MB\n\n"
            "Télécharger et mettre à jour maintenant ?")
        if not rep:
            return

        if not info.get("url_exe"):
            messagebox.showerror(
                "Erreur",
                "Aucun .exe trouvé dans la Release.")
            return

        # Fenêtre de progression
        dlg = ctk.CTkToplevel(self)
        dlg.title("Téléchargement...")
        dlg.configure(fg_color=COULEURS["bg_principal"])
        dlg.geometry("360x120")
        dlg.resizable(False, False)
        dlg.grab_set()

        ctk.CTkLabel(
            dlg, text="Téléchargement en cours…",
            font=POLICES["corps"],
            text_color=COULEURS["texte_principal"]
        ).pack(pady=(16, 8))

        barre = ctk.CTkProgressBar(
            dlg, mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"])
        barre.pack(fill="x", padx=20)
        barre.set(0)

        lbl_pct = ctk.CTkLabel(
            dlg, text="0%",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        lbl_pct.pack()

        def _progres(pct):
            self.after(0, lambda: barre.set(pct / 100))
            self.after(0, lambda: lbl_pct.configure(
                text=f"{pct}%"))

        def _fin(ok, err):
            dlg.after(0, dlg.destroy)
            if ok:
                self.after(0, lambda: messagebox.showinfo(
                    "Mise à jour",
                    "✅ Mise à jour téléchargée !\n"
                    "L'application va redémarrer."))
                self.after(500, self.destroy)
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Erreur", f"Échec : {err}"))

        telecharger_et_remplacer(
            info["url_exe"], _progres, _fin)

    # ── Fermeture + backup ────────────────────────────────
    def _fermeture(self):
        try:
            chemin = faire_backup("fermeture")
            if chemin:
                print(f"[Backup] {chemin}")
        except Exception as ex:
            print(f"[Backup] Erreur : {ex}")
        self.destroy()
