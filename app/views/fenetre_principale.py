# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Fenêtre principale — EPSP ES-SENIA
Gestionnaire de Reliquats de Congé Annuel
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.vue_dashboard import VueDashboard
from app.views.vue_employes import VueEmployes
from app.views.vue_conges import VueConges
from app.views.vue_bordereaux import VueBordereaux

# ── Configuration globale CustomTkinter ───────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FenetrePrincipale(ctk.CTk):
    """
    Fenêtre racine de l'application.
    Architecture : Sidebar fixe à gauche + zone de contenu à droite.
    """

    # Navigation : (clé interne, libellé affiché, icône)
    ONGLETS = [
        ("dashboard",   "Tableau de bord",  "◉"),
        ("employes",    "Employés",          "👤"),
        ("conges",      "Congés & Reliquats","📅"),
        ("bordereaux",  "Bordereaux",        "📄"),
    ]

    def __init__(self):
        super().__init__()
        self._vue_active: str = ""
        self._boutons_nav: dict = {}
        self._vues_cache: dict = {}
        self._configurer_fenetre()
        self._construire_layout()
        self._naviguer("dashboard")

    # ── Configuration fenêtre ─────────────────────────────────────
    def _configurer_fenetre(self):
        self.title("EPSP ES-SENIA — Gestionnaire de Congés Annuels")
        w = DIMENSIONS["fenetre_w"]
        h = DIMENSIONS["fenetre_h"]
        # Centrer sur l'écran
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(DIMENSIONS["fenetre_min_w"], DIMENSIONS["fenetre_min_h"])
        self.configure(fg_color=COULEURS["bg_principal"])

    # ── Layout racine ─────────────────────────────────────────────
    def _construire_layout(self):
        self.grid_columnconfigure(0, weight=0)  # sidebar fixe
        self.grid_columnconfigure(1, weight=1)  # contenu extensible
        self.grid_rowconfigure(0, weight=1)

        self._construire_sidebar()
        self._construire_zone_contenu()

    # ── Sidebar ───────────────────────────────────────────────────
    def _construire_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=DIMENSIONS["sidebar_w"],
            fg_color=COULEURS["bg_sidebar"],
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / en-tête
        frame_logo = ctk.CTkFrame(sidebar, fg_color="transparent")
        frame_logo.pack(fill="x", padx=16, pady=(24, 0))

        # Badge institutionnel
        badge = ctk.CTkFrame(frame_logo,
                             fg_color=COULEURS["accent_bleu"],
                             corner_radius=8,
                             width=44, height=44)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="ES",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF").place(relx=0.5, rely=0.5,
                                                 anchor="center")

        frame_texte = ctk.CTkFrame(frame_logo, fg_color="transparent")
        frame_texte.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(frame_texte, text="EPSP",
                     font=POLICES["titre_app"],
                     text_color=COULEURS["texte_principal"]).pack(anchor="w")
        ctk.CTkLabel(frame_texte, text="ES-SENIA",
                     font=POLICES["petit"],
                     text_color=COULEURS["texte_secondaire"]).pack(anchor="w")

        # Séparateur
        ctk.CTkFrame(sidebar, height=1,
                     fg_color=COULEURS["bordure"]).pack(
                         fill="x", padx=16, pady=(20, 16))

        ctk.CTkLabel(sidebar, text="NAVIGATION",
                     font=("Segoe UI", 9, "bold"),
                     text_color=COULEURS["texte_discret"]).pack(
                         anchor="w", padx=20, pady=(0, 8))

        # Boutons de navigation
        for cle, libelle, icone in self.ONGLETS:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icone}   {libelle}",
                anchor="w",
                fg_color="transparent",
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["sidebar_inact_txt"],
                font=POLICES["nav"],
                height=42,
                corner_radius=8,
                command=lambda c=cle: self._naviguer(c)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._boutons_nav[cle] = btn

        # Pied de sidebar
        frame_pied = ctk.CTkFrame(sidebar, fg_color="transparent")
        frame_pied.pack(side="bottom", fill="x", padx=16, pady=20)
        ctk.CTkFrame(frame_pied, height=1,
                     fg_color=COULEURS["bordure"]).pack(fill="x",
                                                        pady=(0, 12))
        ctk.CTkLabel(frame_pied,
                     text="COPYRIGHT\nILINE TECH 2026\nBY FERAK ALADDIN",
                     font=("Segoe UI", 8),
                     text_color=COULEURS["texte_discret"],
                     justify="center").pack()

    # ── Zone de contenu ───────────────────────────────────────────
    def _construire_zone_contenu(self):
        self.frame_contenu = ctk.CTkFrame(
            self,
            fg_color=COULEURS["bg_principal"],
            corner_radius=0
        )
        self.frame_contenu.grid(row=0, column=1, sticky="nsew")
        self.frame_contenu.grid_rowconfigure(0, weight=1)
        self.frame_contenu.grid_columnconfigure(0, weight=1)

    # ── Navigation ────────────────────────────────────────────────
    def _naviguer(self, cle: str):
        if cle == self._vue_active:
            return

        # Mettre à jour l'état visuel des boutons
        for k, btn in self._boutons_nav.items():
            if k == cle:
                btn.configure(
                    fg_color=COULEURS["sidebar_active_bg"],
                    text_color=COULEURS["sidebar_active_txt"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COULEURS["sidebar_inact_txt"]
                )

        # Masquer la vue précédente
        if self._vue_active and self._vue_active in self._vues_cache:
            self._vues_cache[self._vue_active].grid_remove()

        # Créer ou afficher la vue cible
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
        }
        cls = vues.get(cle)
        if cls is None:
            raise ValueError(f"Vue inconnue : {cle}")
        return cls(self.frame_contenu)
