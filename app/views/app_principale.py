# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import customtkinter as ctk
from tkinter import messagebox
import traceback
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.utils.database import get_config
from app.utils.version import get_version

try:
    from app.config import APP_NAME
except Exception:
    APP_NAME = "TASHIL"

_SW = 220  # Largeur sidebar


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
        self._sb = None
        self._ct = None
        self._construire()
        self._verifier_rollover_auto()
        self._naviguer("dashboard")
        self.bind("<Configure>", self._resize)

    def _construire(self):
        # Sidebar — width dans constructeur UNIQUEMENT
        self._sb = ctk.CTkFrame(
            self,
            width=_SW,
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0)
        self._sb.place(x=0, y=0, relheight=1)
        self._sb.pack_propagate(False)

        # Zone contenu
        self._ct = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0)
        self._ct.place(
            x=_SW, y=0,
            relwidth=1, relheight=1)

        self._remplir_sidebar()

    def _resize(self, _=None):
        try:
            self._ct.place(
                x=_SW, y=0,
                relwidth=1, relheight=1)
        except Exception:
            pass

    def _remplir_sidebar(self):
        sb = self._sb

        # ── Badge ─────────────────────────────────
        # width/height dans constructeur
        badge = ctk.CTkFrame(
            sb,
            width=42, height=42,
            fg_color=COULEURS["accent_bleu"],
            corner_radius=8)
        badge.place(x=12, y=16)
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge, text="T",
            font=("Segoe UI", 18, "bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5,
                anchor="center")

        # Nom app
        poly = get_config("poly_nom") or "TASHIL"
        short = (poly[:15] + "…"
                 if len(poly) > 15 else poly)
        ctk.CTkLabel(
            sb,
            text=f"🇩🇿  {APP_NAME}",
            font=POLICES["titre_app"],
            text_color=COULEURS["texte_principal"]
        ).place(x=62, y=18)
        ctk.CTkLabel(
            sb, text=short,
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).place(x=62, y=40)

        # ── Séparateur 1 ─────────────────────────
        # height dans constructeur, pas dans place()
        sep1 = ctk.CTkFrame(
            sb,
            height=1,
            fg_color=COULEURS["bordure"])
        sep1.place(x=12, y=72,
                   relwidth=1, width=-24)

        ctk.CTkLabel(
            sb, text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=COULEURS["texte_discret"]
        ).place(x=16, y=82)

        # ── Boutons navigation ────────────────────
        y = 102
        for cle, lib, ico in self.ONGLETS:
            if cle in ("service", "admin"):
                sep = ctk.CTkFrame(
                    sb,
                    height=1,
                    fg_color=COULEURS["bordure"])
                sep.place(x=12, y=y,
                          relwidth=1, width=-24)
                y += 10

            # height dans constructeur
            btn = ctk.CTkButton(
                sb,
                height=38,
                text=f"  {ico}   {lib}",
                anchor="w",
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS[
                    "sidebar_inact_txt"],
                font=POLICES["nav"],
                corner_radius=8,
                command=lambda c=cle:
                    self._naviguer(c))
            btn.place(x=8, y=y,
                      relwidth=1, width=-16)
            self._boutons_nav[cle] = btn
            y += 44

        # ── Pied sidebar ──────────────────────────
        # Frame conteneur pied — height constructeur
        pied = ctk.CTkFrame(
            sb,
            height=72,
            fg_color="transparent")
        pied.place(x=0, rely=1.0,
                   relwidth=1, y=-72)
        pied.pack_propagate(False)

        # Séparateur pied — height constructeur
        sep_pied = ctk.CTkFrame(
            pied,
            height=1,
            fg_color=COULEURS["bordure"])
        sep_pied.place(x=12, y=0,
                       relwidth=1, width=-24)

        # Bouton MAJ — height dans constructeur
        self.btn_maj = ctk.CTkButton(
            pied,
            height=26,
            text="🔄  Vérifier les mises à jour",
            fg_color="transparent",
            hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_discret"],
            font=("Segoe UI", 9),
            corner_radius=6,
            command=self._verifier_maj)
        self.btn_maj.place(
            x=6, y=8,
            relwidth=1, width=-12)

        ctk.CTkLabel(
            pied,
            text=f"v{get_version()}  •  "
                 "ILINE TECH 2026",
            font=("Segoe UI", 8),
            text_color=COULEURS["texte_discret"],
            justify="center"
        ).place(relx=0.5, y=42, anchor="n")

    # ── Navigation ────────────────────────────────
    def _naviguer(self, cle: str):
        if cle == self._vue_active:
            return

        for k, b in self._boutons_nav.items():
            if k == cle:
                b.configure(
                    fg_color=COULEURS[
                        "sidebar_active_bg"],
                    text_color=COULEURS[
                        "sidebar_active_txt"])
            elif "⚠" not in b.cget("text"):
                b.configure(
                    fg_color="transparent",
                    text_color=COULEURS[
                        "sidebar_inact_txt"])

        if (self._vue_active and
                self._vue_active in
                self._vues_cache):
            try:
                self._vues_cache[
                    self._vue_active
                ].place_forget()
            except Exception:
                pass

        if cle not in self._vues_cache:
            try:
                vue = self._creer_vue(cle)
                vue.place(x=0, y=0,
                          relwidth=1,
                          relheight=1)
                self._vues_cache[cle] = vue
            except Exception:
                print(f"[ERR {cle}]\n"
                      f"{traceback.format_exc()}")
                return
        else:
            self._vues_cache[cle].place(
                x=0, y=0,
                relwidth=1, relheight=1)
            if not self._modal_actif():
                try:
                    self._vues_cache[
                        cle].rafraichir()
                except Exception:
                    pass

        self._vue_active = cle
        try:
            self._ct.update_idletasks()
        except Exception:
            pass

    def _modal_actif(self) -> bool:
        try:
            for w in self.winfo_toplevel(
            ).winfo_children():
                if isinstance(
                        w, ctk.CTkToplevel):
                    if w.winfo_exists():
                        return True
        except Exception:
            pass
        return False

    def _creer_vue(self, cle: str):
        from app.views.vue_dashboard import (
            VueDashboard)
        from app.views.vue_employes import (
            VueEmployes)
        from app.views.vue_conge import VueConge
        from app.views.vue_reliquat import (
            VueReliquat)
        from app.views.vue_bordereau import (
            VueBordereau)
        from app.views.vue_tableau_service import (
            VueTableauService)
        from app.views.vue_administration import (
            VueAdministration)

        vues = {
            "dashboard":  VueDashboard,
            "employes":   VueEmployes,
            "conge":      VueConge,
            "reliquat":   VueReliquat,
            "bordereau":  VueBordereau,
            "service":    VueTableauService,
            "admin":      VueAdministration,
        }
        cls = vues.get(cle)
        if not cls:
            raise ValueError(
                f"Vue inconnue: {cle}")
        return cls(self._ct)

    def _verifier_rollover_auto(self):
        try:
            from app.utils.deduction_engine import (
                verifier_rollover_necessaire)
            if verifier_rollover_necessaire():
                b = self._boutons_nav.get("admin")
                if b:
                    b.configure(
                        text="  ⚙   Administration ⚠",
                        text_color=COULEURS[
                            "accent_orange"])
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
                    text="🔄  Vérifier "
                         "les mises à jour"))
            if not info:
                self.after(0, lambda:
                    messagebox.showwarning(
                        "Mise à jour",
                        "Pas de connexion."))
                return
            tag = info.get("tag", "")
            if version_plus_recente(tag):
                self.after(0, lambda:
                    self._proposer_maj(info))
            else:
                self.after(0, lambda:
                    messagebox.showinfo(
                        "✅  À jour",
                        f"v{get_version()} — "
                        f"Distante : {tag}"))

        verifier_en_arriere_plan(_cb)

    def _proposer_maj(self, info: dict):
        from app.utils.updater import (
            telecharger_et_remplacer)
        tag     = info.get("tag", "")
        url_exe = info.get("url_exe", "")
        taille  = round(
            info.get("taille", 0)
            / 1024 / 1024, 1)
        if not url_exe:
            messagebox.showerror(
                "Erreur", "Aucun .exe trouvé.")
            return
        if not messagebox.askyesno(
                f"🆕  {tag}",
                f"Nouvelle version : {tag}\n"
                f"Taille : {taille} MB\n\n"
                "Installer maintenant ?"):
            return

        # Fenêtre progression
        dlg = ctk.CTkToplevel(self)
        dlg.title("Mise à jour…")
        dlg.configure(
            fg_color=COULEURS["bg_principal"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        dlg.protocol(
            "WM_DELETE_WINDOW", lambda: None)
        dlg.geometry("380x130")

        ctk.CTkLabel(
            dlg,
            text=f"Téléchargement {tag}…",
            font=POLICES["sous_titre"],
            text_color=COULEURS["texte_principal"]
        ).place(relx=0.5, y=16, anchor="n")

        barre = ctk.CTkProgressBar(
            dlg,
            height=12,
            mode="determinate",
            fg_color=COULEURS["bg_champ"],
            progress_color=COULEURS["accent_bleu"],
            corner_radius=6)
        barre.place(x=24, y=52,
                    relwidth=1, width=-48)
        barre.set(0)

        lbl = ctk.CTkLabel(
            dlg, text="0 %",
            font=POLICES["corps_bold"],
            text_color=COULEURS["accent_bleu"])
        lbl.place(relx=0.5, y=76, anchor="n")

        def _p(pct):
            self.after(0, lambda p=pct: (
                barre.set(p / 100),
                lbl.configure(text=f"{p} %")))

        def _f(ok, err):
            self.after(0, lambda:
                self._fin_maj(dlg, ok, err))

        telecharger_et_remplacer(
            url_exe, _p, _f)

    def _fin_maj(self, dlg, ok, err):
        try:
            dlg.destroy()
        except Exception:
            pass
        if ok:
            messagebox.showinfo(
                "✅", "Redémarrage en cours…")
            self.after(600, self._quitter_maj)
        else:
            messagebox.showerror(
                "❌  Échec", str(err))

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
