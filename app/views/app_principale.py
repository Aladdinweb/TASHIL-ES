# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
AppPrincipale — 7 onglets navigation
Congé et Reliquat sont séparés.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_config
from app.utils.version import get_version


class AppPrincipale(ctk.CTkFrame):
    ONGLETS = [
        ("dashboard", "Tableau de bord", "◉"),
        ("employes",  "Employés",         "👤"),
        ("conge",     "Congés",           "📅"),
        ("reliquat",  "Reliquats",        "🗂"),
        ("bordereau", "Bordereau",        "📄"),
        ("service",   "Tableau Service",  "📋"),
        ("admin",     "Administration",   "⚙"),
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
        self._construire_zone_contenu()
        self._verifier_rollover_auto()
        self._naviguer("dashboard")

    def _construire_sidebar(self):
        sb = ctk.CTkFrame(
            self,
            width=DIMENSIONS["sidebar_w"],
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # Logo
        fl = ctk.CTkFrame(sb, fg_color="transparent")
        fl.pack(fill="x", padx=16, pady=(24, 0))
        badge = ctk.CTkFrame(
            fl,
            fg_color=COULEURS["accent_bleu"],
            corner_radius=8, width=44, height=44)
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
        ).pack(fill="x", padx=16, pady=(18, 14))

        ctk.CTkLabel(
            sb, text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=COULEURS["texte_discret"]
        ).pack(anchor="w", padx=20, pady=(0, 8))

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
                font=POLICES["nav"], height=42,
                corner_radius=8,
                command=lambda c=cle:
                    self._naviguer(c))
            btn.pack(fill="x", padx=12, pady=2)
            self._boutons_nav[cle] = btn

        # Pied
        fp = ctk.CTkFrame(sb,
                          fg_color="transparent")
        fp.pack(side="bottom", fill="x",
                padx=16, pady=18)
        ctk.CTkFrame(
            fp, height=1,
            fg_color=COULEURS["bordure"]
        ).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(
            fp,
            text="🔄  Vérifier les mises à jour",
            fg_color="transparent",
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_discret"],
            font=("Segoe UI", 9), height=26,
            corner_radius=6,
            command=self._verifier_maj
        ).pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(
            fp,
            text=f"v{get_version()}  •  "
                 "ILINE TECH 2026\nBY FERAK ALADDIN",
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
        self.frame_contenu.grid_rowconfigure(
            0, weight=1)
        self.frame_contenu.grid_columnconfigure(
            0, weight=1)

    def _naviguer(self, cle: str):
        if cle == self._vue_active:
            return
        for k, btn in self._boutons_nav.items():
            if k == cle:
                btn.configure(
                    fg_color=COULEURS["sidebar_active_bg"],
                    text_color=COULEURS["sidebar_active_txt"])
            else:
                t = btn.cget("text")
                if "⚠" not in t:
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

    def _creer_vue(self, cle: str):
        from app.views.vue_dashboard import (
            VueDashboard)
        from app.views.vue_employes import (
            VueEmployes)
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

    def _verifier_maj(self):
        try:
            from app.utils.updater import (
                verifier_en_arriere_plan,
                version_plus_recente)

            def _cb(info):
                if info is None:
                    self.after(0, lambda:
                        messagebox.showinfo(
                            "Mise à jour",
                            "Pas de connexion."))
                    return
                tag = info.get("tag", "")
                if version_plus_recente(tag):
                    self.after(0, lambda:
                        messagebox.showinfo(
                            "Nouvelle version",
                            f"Version {tag} disponible !\n"
                            "Téléchargez dans Releases."))
                else:
                    self.after(0, lambda:
                        messagebox.showinfo(
                            "À jour",
                            f"✅ Version actuelle : "
                            f"v{get_version()}\n"
                            f"Distante : {tag}"))

            verifier_en_arriere_plan(_cb)
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _verifier_maj(self):
        try:
            from app.utils.updater import (
                verifier_en_arriere_plan,
                version_plus_recente)

            def _cb(info):
                if info is None:
                    self.after(0, lambda:
                        messagebox.showinfo(
                            "Mise à jour",
                            "Impossible de vérifier.\n"
                            "Vérifiez votre connexion."))
                    return
                tag = info.get("tag", "")
                if version_plus_recente(tag):
                    self.after(
                        0,
                        lambda: self._proposer_maj(
                            info))
                else:
                    self.after(0, lambda:
                        messagebox.showinfo(
                            "✅ À jour",
                            f"Vous utilisez la "
                            f"dernière version.\n"
                            f"Version : v{get_version()}"))

            verifier_en_arriere_plan(_cb)
        except Exception as ex:
            messagebox.showerror("Erreur", str(ex))

    def _proposer_maj(self, info: dict):
        from app.utils.updater import (
            telecharger_et_remplacer)

        tag     = info.get("tag", "")
        taille  = info.get("taille", 0)
        taille_mb = round(taille / 1024 / 1024, 1)
        notes   = info.get("notes", "")[:200]
        url_exe = info.get("url_exe", "")

        if not url_exe:
            messagebox.showerror(
                "Erreur",
                "Aucun fichier .exe trouvé "
                "dans cette Release.")
            return

        rep = messagebox.askyesno(
            "🔄  Nouvelle version disponible",
            f"Version {tag} disponible !\n\n"
            f"Taille : {taille_mb} MB\n\n"
            f"{notes}\n\n"
            "Télécharger et installer "
            "automatiquement ?\n"
            "(L'application redémarrera.)")
        if not rep:
            return

        # Fenêtre de progression
        dlg = ctk.CTkToplevel(self)
        dlg.title("Mise à jour en cours…")
        dlg.configure(
            fg_color=COULEURS["bg_principal"])
        dlg.geometry("380x150")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(
            dlg,
            text=f"Téléchargement {tag}…",
            font=POLICES["corps"],
            text_color=COULEURS["texte_principal"]
        ).pack(pady=(18, 8))

        barre = ctk.CTkProgressBar(
            dlg, mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"],
            height=12, corner_radius=6)
        barre.pack(fill="x", padx=24)
        barre.set(0)

        lbl_pct = ctk.CTkLabel(
            dlg, text="0%",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"])
        lbl_pct.pack(pady=6)

        lbl_info = ctk.CTkLabel(
            dlg, text="Connexion au serveur…",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"])
        lbl_info.pack()

        def _prog(pct):
            self.after(
                0,
                lambda: barre.set(pct / 100))
            self.after(
                0,
                lambda: lbl_pct.configure(
                    text=f"{pct}%"))
            if pct < 100:
                self.after(
                    0,
                    lambda: lbl_info.configure(
                        text=f"Téléchargement… "
                             f"{pct}%"))
            else:
                self.after(
                    0,
                    lambda: lbl_info.configure(
                        text="Préparation du "
                             "remplacement…"))

        def _fin(ok, err):
            self.after(0, lambda: _on_fin(ok, err))

        def _on_fin(ok, err):
            try:
                dlg.destroy()
            except Exception:
                pass
            if ok:
                messagebox.showinfo(
                    "✅ Mise à jour réussie",
                    "La nouvelle version a été "
                    "téléchargée.\n\n"
                    "L'application va se fermer "
                    "et redémarrer "
                    "automatiquement.")
                self.after(800, self._quitter)
            else:
                messagebox.showerror(
                    "Erreur de mise à jour",
                    f"La mise à jour a échoué :\n"
                    f"{err}\n\n"
                    "Téléchargez manuellement sur :\n"
                    "github.com/Aladdinweb/"
                    "epsp-conge-manager/releases")

        telecharger_et_remplacer(
            url_exe, _prog, _fin)

    def _quitter(self):
        from app.utils.database import faire_backup
        try:
            faire_backup("avant_maj")
        except Exception:
            pass
        # Fermer proprement — le .bat
        # relancera l'app
        import os, sys
        os._exit(0)

    def rafraichir(self):
        pass
