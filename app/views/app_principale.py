# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
AppPrincipale — Navigation + Mise à jour automatique
"""
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_config
from app.utils.version import get_version


class AppPrincipale(ctk.CTkFrame):
    ONGLETS = [
        ("dashboard", "Tableau de bord", "◉"),
        ("employes",  "Employés",        "👤"),
        ("conge",     "Congés",          "📅"),
        ("reliquat",  "Reliquats",       "🗂"),
        ("bordereau", "Bordereau",       "📄"),
        ("service",   "Tableau Service", "📋"),
        ("admin",     "Administration",  "⚙"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._vue_active  = ""
        self._boutons_nav = {}
        self._vues_cache  = {}
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._construire_sidebar()
        self._construire_contenu()
        self._verifier_rollover_auto()
        self._naviguer("dashboard")

    # ── Sidebar ───────────────────────────────────
    def _construire_sidebar(self):
        sb = ctk.CTkFrame(
            self,
            width=DIMENSIONS["sidebar_w"],
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Logo
        fl = ctk.CTkFrame(sb,
                          fg_color="transparent")
        fl.pack(fill="x", padx=16,
                pady=(24, 0))
        badge = ctk.CTkFrame(
            fl, fg_color=COULEURS["accent_bleu"],
            corner_radius=8,
            width=44, height=44)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text="ES",
            font=("Segoe UI", 16, "bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5,
                anchor="center")

        ft = ctk.CTkFrame(fl,
                          fg_color="transparent")
        ft.pack(side="left", padx=(10, 0))
        poly = get_config("poly_nom") or "ES-SENIA"
        ctk.CTkLabel(
            ft, text="🇩🇿  EPSP",
            font=POLICES["titre_app"],
            text_color=COULEURS["texte_principal"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            ft,
            text=(poly[:16] + "…"
                  if len(poly) > 16 else poly),
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        ctk.CTkFrame(
            sb, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", padx=16,
               pady=(18, 14))

        ctk.CTkLabel(
            sb, text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=COULEURS["texte_discret"]
        ).pack(anchor="w", padx=20,
               pady=(0, 8))

        for cle, libelle, icone in self.ONGLETS:
            if cle in ("service", "admin"):
                ctk.CTkFrame(
                    sb, height=1,
                    fg_color=COULEURS["bordure"]
                ).pack(fill="x", padx=16,
                       pady=(6, 6))
            btn = ctk.CTkButton(
                sb,
                text=f"  {icone}   {libelle}",
                anchor="w",
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["sidebar_inact_txt"],
                font=POLICES["nav"],
                height=42, corner_radius=8,
                command=lambda c=cle:
                    self._naviguer(c))
            btn.pack(fill="x", padx=12, pady=2)
            self._boutons_nav[cle] = btn

        # Pied sidebar
        fp = ctk.CTkFrame(sb,
                          fg_color="transparent")
        fp.pack(side="bottom", fill="x",
                padx=16, pady=18)
        ctk.CTkFrame(
            fp, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", pady=(0, 8))

        # Bouton MAJ
        self.btn_maj = ctk.CTkButton(
            fp,
            text="🔄  Vérifier les mises à jour",
            fg_color="transparent",
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_discret"],
            font=("Segoe UI", 9),
            height=28, corner_radius=6,
            command=self._verifier_maj)
        self.btn_maj.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            fp,
            text=f"v{get_version()}  •  "
                 "ILINE TECH 2026\nBY FERAK ALADDIN",
            font=("Segoe UI", 8),
            text_color=COULEURS["texte_discret"],
            justify="center"
        ).pack()

    def _construire_contenu(self):
        self.frame_contenu = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0)
        self.frame_contenu.grid(
            row=0, column=1, sticky="nsew")
        self.frame_contenu.grid_rowconfigure(
            0, weight=1)
        self.frame_contenu.grid_columnconfigure(
            0, weight=1)

    # ── Navigation ────────────────────────────────
    def _naviguer(self, cle: str):
        if cle == self._vue_active:
            return
        for k, btn in self._boutons_nav.items():
            if k == cle:
                btn.configure(
                    fg_color=COULEURS["sidebar_active_bg"],
                    text_color=COULEURS["sidebar_active_txt"])
            else:
                if "⚠" not in btn.cget("text"):
                    btn.configure(
                        fg_color="transparent",
                        text_color=COULEURS["sidebar_inact_txt"])
        if (self._vue_active and
                self._vue_active in self._vues_cache):
            self._vues_cache[
                self._vue_active].grid_remove()
        if cle not in self._vues_cache:
            vue = self._creer_vue(cle)
            vue.grid(row=0, column=0,
                     sticky="nsew")
            self._vues_cache[cle] = vue
        else:
            self._vues_cache[cle].grid()
            try:
                self._vues_cache[cle].rafraichir()
            except Exception:
                pass
        self._vue_active = cle
        self.update_idletasks()

    def _creer_vue(self, cle: str):
        from app.views.vue_dashboard import VueDashboard
        from app.views.vue_employes import VueEmployes
        from app.views.vue_conge import VueConge
        from app.views.vue_reliquat import VueReliquat
        from app.views.vue_bordereau_maintenance import (
            VueBordereauMaintenance)
        from app.views.vue_tableau_service import (
            VueTableauService)
        from app.views.vue_administration import (
            VueAdministration)
        vues = {
            "dashboard":  VueDashboard,
            "employes":   VueEmployes,
            "conge":      VueConge,
            "reliquat":   VueReliquat,
            "bordereau":  VueBordereauMaintenance,
            "service":    VueTableauService,
            "admin":      VueAdministration,
        }
        cls = vues.get(cle)
        if not cls:
            raise ValueError(f"Vue inconnue: {cle}")
        return cls(self.frame_contenu)

    def _verifier_rollover_auto(self):
        try:
            from app.utils.deduction_engine import (
                verifier_rollover_necessaire)
            if verifier_rollover_necessaire():
                btn = self._boutons_nav.get("admin")
                if btn:
                    btn.configure(
                        text="  ⚙   Administration ⚠",
                        text_color=COULEURS["accent_orange"])
        except Exception:
            pass

    # ══════════════════════════════════════════════
    # SYSTÈME DE MISE À JOUR AUTOMATIQUE
    # ══════════════════════════════════════════════

    def _verifier_maj(self):
        """Lance la vérification en arrière-plan."""
        # Désactiver le bouton pendant la vérif
        self.btn_maj.configure(
            state="disabled",
            text="⏳  Vérification…")

        from app.utils.updater import (
            verifier_en_arriere_plan,
            version_plus_recente)

        def _cb(info):
            # Réactiver le bouton
            self.after(0, lambda:
                self.btn_maj.configure(
                    state="normal",
                    text="🔄  Vérifier les mises à jour"))

            if info is None:
                self.after(0, lambda:
                    messagebox.showwarning(
                        "Mise à jour",
                        "Impossible de contacter GitHub.\n"
                        "Vérifiez votre connexion internet."))
                return

            tag = info.get("tag", "")
            url = info.get("url_exe", "")

            if not tag:
                self.after(0, lambda:
                    messagebox.showwarning(
                        "Mise à jour",
                        "Impossible de lire la version."))
                return

            if version_plus_recente(tag):
                # Nouvelle version → proposer MAJ
                self.after(0, lambda:
                    self._proposer_maj(info))
            else:
                self.after(0, lambda:
                    messagebox.showinfo(
                        "✅  Application à jour",
                        f"Vous utilisez la dernière version.\n\n"
                        f"Version installée : v{get_version()}\n"
                        f"Version distante  : {tag}"))

        verifier_en_arriere_plan(_cb)

    def _proposer_maj(self, info: dict):
        """
        Propose le téléchargement et l'installation
        automatique de la nouvelle version.
        """
        tag      = info.get("tag", "")
        url_exe  = info.get("url_exe", "")
        taille   = info.get("taille", 0)
        notes    = info.get("notes", "")[:300]
        taille_mb = round(taille / 1024 / 1024, 1)

        if not url_exe:
            messagebox.showerror(
                "Erreur",
                "Aucun fichier .exe trouvé "
                "dans la Release.\n"
                "Téléchargez manuellement sur GitHub.")
            return

        msg = (
            f"🆕  Nouvelle version : {tag}\n\n"
            f"Version actuelle : v{get_version()}\n"
            f"Taille du fichier : {taille_mb} MB\n\n"
        )
        if notes:
            msg += f"Notes :\n{notes}\n\n"
        msg += (
            "Voulez-vous télécharger et installer\n"
            "la mise à jour automatiquement ?\n\n"
            "L'application redémarrera après."
        )

        rep = messagebox.askyesno(
            "Mise à jour disponible", msg)

        if not rep:
            return

        self._lancer_telechargement(url_exe, tag)

    def _lancer_telechargement(
            self, url_exe: str, tag: str):
        """
        Ouvre la fenêtre de progression et lance
        le téléchargement.
        """
        from app.utils.updater import (
            telecharger_et_remplacer)

        # Fenêtre progression
        dlg = ctk.CTkToplevel(self)
        dlg.title(f"Téléchargement {tag}…")
        dlg.configure(
            fg_color=COULEURS["bg_principal"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.protocol(
            "WM_DELETE_WINDOW", lambda: None)

        w, h = 420, 180
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth()  - w) // 2
        y = (dlg.winfo_screenheight() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        ctk.CTkLabel(
            dlg,
            text=f"Téléchargement de la version "
                 f"{tag}…",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(pady=(20, 10))

        barre = ctk.CTkProgressBar(
            dlg, mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"],
            height=16, corner_radius=8)
        barre.pack(fill="x", padx=30)
        barre.set(0)

        lbl_pct = ctk.CTkLabel(
            dlg, text="0 %",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"])
        lbl_pct.pack(pady=4)

        lbl_info = ctk.CTkLabel(
            dlg,
            text="Connexion au serveur GitHub…",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        lbl_info.pack()

        # Callbacks thread-safe
        def _prog(pct: int):
            self.after(0, lambda p=pct: (
                barre.set(p / 100),
                lbl_pct.configure(
                    text=f"{p} %"),
                lbl_info.configure(
                    text=("Finalisation…"
                          if p >= 100
                          else f"Téléchargement… {p} %")),
            ))

        def _fin(ok: bool, err: str):
            self.after(0, lambda:
                self._apres_telechargement(
                    dlg, ok, err))

        telecharger_et_remplacer(
            url_exe, _prog, _fin)

    def _apres_telechargement(
            self, dlg, ok: bool, err: str):
        """Appelé après la fin du téléchargement."""
        try:
            dlg.destroy()
        except Exception:
            pass

        if ok:
            messagebox.showinfo(
                "✅  Mise à jour réussie",
                "La nouvelle version a été "
                "téléchargée avec succès.\n\n"
                "L'application va se fermer et "
                "redémarrer automatiquement.\n\n"
                "Merci de patienter 5 secondes.")
            # Backup DB puis fermeture
            self.after(500, self._fermer_pour_maj)
        else:
            messagebox.showerror(
                "❌  Échec de la mise à jour",
                f"Le téléchargement a échoué :\n"
                f"{err}\n\n"
                "Téléchargez manuellement sur :\n"
                "github.com/Aladdinweb/"
                "epsp-conge-manager/releases")

    def _fermer_pour_maj(self):
        """Backup + fermeture propre pour MAJ."""
        try:
            from app.utils.database import (
                faire_backup)
            faire_backup("avant_maj")
        except Exception:
            pass
        # os._exit pour laisser le .bat travailler
        import os
        os._exit(0)

    def rafraichir(self):
        pass

    def _proposer_maj(self, info: dict):
        from app.utils.updater import (
            telecharger_et_remplacer)
        tag     = info.get("tag", "")
        url_exe = info.get("url_exe", "")
        taille  = info.get("taille", 0)
        taille_mb = round(taille / 1024 / 1024, 1)

        if not url_exe:
            messagebox.showerror(
                "Erreur",
                "Aucun .exe dans cette Release.\n"
                "Téléchargez manuellement sur GitHub.")
            return

        rep = messagebox.askyesno(
            f"🆕  Version {tag} disponible",
            f"Version actuelle : v{get_version()}\n"
            f"Nouvelle version : {tag}\n"
            f"Taille : {taille_mb} MB\n\n"
            "Télécharger et installer maintenant ?\n"
            "(L'application redémarrera après.)")
        if not rep:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Téléchargement…")
        dlg.configure(
            fg_color=COULEURS["bg_principal"])
        dlg.geometry("400x160")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.protocol("WM_DELETE_WINDOW",
                     lambda: None)
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth()  - 400) // 2
        y = (dlg.winfo_screenheight() - 160) // 2
        dlg.geometry(f"400x160+{x}+{y}")

        ctk.CTkLabel(
            dlg,
            text=f"Téléchargement {tag}…",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).pack(pady=(18, 8))

        barre = ctk.CTkProgressBar(
            dlg, mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"],
            height=14, corner_radius=6)
        barre.pack(fill="x", padx=30)
        barre.set(0)

        lbl = ctk.CTkLabel(
            dlg, text="0 %",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"])
        lbl.pack(pady=6)

        def _prog(pct):
            self.after(0, lambda p=pct: (
                barre.set(p / 100),
                lbl.configure(text=f"{p} %")))

        def _fin(ok, err):
            self.after(0, lambda:
                       self._fin_telechargement(
                           dlg, ok, err))

        telecharger_et_remplacer(
            url_exe, _prog, _fin)

    def _fin_telechargement(
            self, dlg, ok: bool, err: str):
        try:
            dlg.destroy()
        except Exception:
            pass
        if ok:
            messagebox.showinfo(
                "✅  Mise à jour réussie",
                "Téléchargement terminé.\n"
                "L'application va redémarrer.")
            self.after(600, self._quitter_pour_maj)
        else:
            messagebox.showerror(
                "❌  Échec",
                f"Erreur : {err}\n\n"
                "Téléchargez manuellement :\n"
                "github.com/Aladdinweb/"
                "epsp-conge-manager/releases")

    def _quitter_pour_maj(self):
        try:
            from app.utils.database import (
                faire_backup)
            faire_backup("avant_maj")
        except Exception:
            pass
        import os
        os._exit(0)
