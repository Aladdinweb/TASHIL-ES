# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""AppPrincipale TASHIL — place() uniquement"""
import customtkinter as ctk
from tkinter import messagebox
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_config
from app.utils.version import get_version

try:
    from app.config import APP_NAME
except Exception:
    APP_NAME = "TASHIL"


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
    SIDEBAR_W = DIMENSIONS["sidebar_w"]

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0, **kwargs)
        self._vue_active  = ""
        self._boutons_nav = {}
        self._vues_cache  = {}

        # place() interne
        self._sidebar_frame = None
        self._content_frame = None

        self._construire()
        self._verifier_rollover_auto()
        self._naviguer("dashboard")

        # Bind resize
        self.bind("<Configure>", self._on_resize)

    def _construire(self):
        # Sidebar
        self._sidebar_frame = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0)
        self._sidebar_frame.place(
            x=0, y=0,
            relheight=1,
            width=self.SIDEBAR_W)

        # Contenu
        self._content_frame = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0)
        self._content_frame.place(
            x=self.SIDEBAR_W, y=0,
            relheight=1,
            relwidth=1,
            width=-self.SIDEBAR_W)

        self._construire_sidebar()

    def _on_resize(self, event):
        """Maintient le layout place() au resize."""
        try:
            if self._content_frame:
                self._content_frame.place(
                    x=self.SIDEBAR_W, y=0,
                    relheight=1,
                    relwidth=1,
                    width=-self.SIDEBAR_W)
        except Exception:
            pass

    def _construire_sidebar(self):
        sb = self._sidebar_frame

        # Logo TASHIL
        fl = ctk.CTkFrame(sb,
                          fg_color="transparent")
        fl.place(x=0, y=0,
                 relwidth=1, height=90)

        badge = ctk.CTkFrame(
            fl,
            fg_color=COULEURS["accent_bleu"],
            corner_radius=8,
            width=44, height=44)
        badge.place(x=14, y=23)
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text="T",
            font=("Segoe UI", 20, "bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5,
                anchor="center")

        ctk.CTkLabel(
            fl,
            text=f"🇩🇿  {APP_NAME}",
            font=POLICES["titre_app"],
            text_color=COULEURS["texte_principal"]
        ).place(x=68, y=24)

        poly = get_config("poly_nom") or "ES-SENIA"
        short = (poly[:16] + "…"
                 if len(poly) > 16 else poly)
        ctk.CTkLabel(
            fl, text=short,
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=68, y=46)

        # Séparateur
        sep = ctk.CTkFrame(
            sb, fg_color=COULEURS["bordure"],
            height=1)
        sep.place(x=16, y=94,
                  relwidth=1, width=-32)

        # Label NAVIGATION
        ctk.CTkLabel(
            sb, text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=COULEURS["texte_discret"]
        ).place(x=20, y=108)

        # Boutons navigation
        y_pos = 130
        for cle, libelle, icone in self.ONGLETS:
            if cle in ("service", "admin"):
                sep2 = ctk.CTkFrame(
                    sb,
                    fg_color=COULEURS["bordure"],
                    height=1)
                sep2.place(x=16, y=y_pos,
                           relwidth=1, width=-32)
                y_pos += 10

            btn = ctk.CTkButton(
                sb,
                text=f"  {icone}   {libelle}",
                anchor="w",
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["sidebar_inact_txt"],
                font=POLICES["nav"],
                height=40,
                corner_radius=8,
                command=lambda c=cle:
                    self._naviguer(c))
            btn.place(x=10, y=y_pos,
                      relwidth=1, width=-20)
            self._boutons_nav[cle] = btn
            y_pos += 46

        # Pied sidebar
        fp = ctk.CTkFrame(
            sb, fg_color="transparent")
        fp.place(x=0, rely=1.0,
                 relwidth=1, height=90,
                 y=-90)

        ctk.CTkFrame(
            fp, fg_color=COULEURS["bordure"],
            height=1
        ).place(x=16, y=0,
                relwidth=1, width=-32)

        self.btn_maj = ctk.CTkButton(
            fp,
            text="🔄  Vérifier les mises à jour",
            fg_color="transparent",
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_discret"],
            font=("Segoe UI", 9),
            height=26, corner_radius=6,
            command=self._verifier_maj)
        self.btn_maj.place(x=8, y=10,
                           relwidth=1, width=-16)

        ctk.CTkLabel(
            fp,
            text=f"v{get_version()}  •  "
                 "ILINE TECH 2026",
            font=("Segoe UI", 8),
            text_color=COULEURS["texte_discret"],
            justify="center"
        ).place(relx=0.5, y=44, anchor="n")

    # ── Navigation ────────────────────────────
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
            try:
                self._vues_cache[
                    self._vue_active].place_forget()
            except Exception:
                pass

        if cle not in self._vues_cache:
            try:
                vue = self._creer_vue(cle)
                vue.place(x=0, y=0,
                          relwidth=1, relheight=1,
                          in_=self._content_frame)
                self._vues_cache[cle] = vue
            except Exception as ex:
                import traceback
                print(f"[ERR vue {cle}] "
                      f"{traceback.format_exc()}")
                return
        else:
            self._vues_cache[cle].place(
                x=0, y=0,
                relwidth=1, relheight=1,
                in_=self._content_frame)
            try:
                self._vues_cache[cle].rafraichir()
            except Exception:
                pass

        self._vue_active = cle
        self._content_frame.update_idletasks()

    def _creer_vue(self, cle: str):
        from app.views.vue_dashboard import (
            VueDashboard)
        from app.views.vue_employes import (
            VueEmployes)
        from app.views.vue_conge import VueConge
        from app.views.vue_reliquat import (
            VueReliquat)
        from app.views.vue_bordereau_maintenance\
            import VueBordereauMaintenance
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
            raise ValueError(
                f"Vue inconnue: {cle}")
        return cls(self._content_frame)

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
        self.btn_maj.configure(
            state="disabled",
            text="⏳  Vérification…")

        from app.utils.updater import (
            verifier_en_arriere_plan,
            version_plus_recente)

        def _cb(info):
            self.after(0, lambda:
                self.btn_maj.configure(
                    state="normal",
                    text="🔄  Vérifier les mises à jour"))

            if not info:
                self.after(0, lambda:
                    messagebox.showwarning(
                        "Mise à jour",
                        "Pas de connexion internet."))
                return

            tag = info.get("tag", "")
            if version_plus_recente(tag):
                self.after(0, lambda:
                    self._proposer_maj(info))
            else:
                self.after(0, lambda:
                    messagebox.showinfo(
                        "✅  À jour",
                        f"Version actuelle : "
                        f"v{get_version()}\n"
                        f"Distante : {tag}"))

        verifier_en_arriere_plan(_cb)

    def _proposer_maj(self, info: dict):
        from app.utils.updater import (
            telecharger_et_remplacer)

        tag      = info.get("tag", "")
        url_exe  = info.get("url_exe", "")
        taille   = info.get("taille", 0)
        taille_mb = round(taille / 1024 / 1024, 1)

        if not url_exe:
            messagebox.showerror(
                "Erreur",
                "Aucun .exe dans cette Release.")
            return

        rep = messagebox.askyesno(
            f"🆕  {tag} disponible",
            f"Nouvelle version : {tag}\n"
            f"Taille : {taille_mb} MB\n\n"
            "Télécharger et installer ?")
        if not rep:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Téléchargement…")
        dlg.configure(
            fg_color=COULEURS["bg_principal"])
        dlg.geometry("400x150")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.protocol("WM_DELETE_WINDOW",
                     lambda: None)

        ctk.CTkLabel(
            dlg,
            text=f"Téléchargement {tag}…",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).place(relx=0.5, y=20, anchor="n")

        barre = ctk.CTkProgressBar(
            dlg, mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"],
            height=14, corner_radius=6)
        barre.place(x=24, y=60,
                    relwidth=1, width=-48)
        barre.set(0)

        lbl = ctk.CTkLabel(
            dlg, text="0 %",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"])
        lbl.place(relx=0.5, y=90, anchor="n")

        def _prog(pct):
            self.after(0, lambda p=pct: (
                barre.set(p / 100),
                lbl.configure(text=f"{p} %")))

        def _fin(ok, err):
            self.after(0, lambda:
                self._fin_maj(dlg, ok, err))

        telecharger_et_remplacer(
            url_exe, _prog, _fin)

    def _fin_maj(self, dlg, ok, err):
        try:
            dlg.destroy()
        except Exception:
            pass
        if ok:
            messagebox.showinfo(
                "✅  Mise à jour",
                "Téléchargement terminé.\n"
                "L'application va redémarrer.")
            self.after(600, self._quitter_maj)
        else:
            messagebox.showerror(
                "❌  Échec", f"{err}")

    def _quitter_maj(self):
        try:
            from app.utils.database import (
                faire_backup)
            faire_backup("avant_maj")
        except Exception:
            pass
        import os
        os._exit(0)

    def rafraichir(self):
        pass
