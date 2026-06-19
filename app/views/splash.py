# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Splash Screen — EPSP ES-SENIA
Drapeau algérien animé avant le chargement.
"""
import customtkinter as ctk
import threading
import time
from app.utils.theme import COULEURS
from app.utils.version import get_full_label


class SplashScreen(ctk.CTkToplevel):
    """
    Fenêtre splash affichée au démarrage.
    S'auto-ferme après `duree_ms` millisecondes.
    callback() est appelé à la fermeture.
    """

    def __init__(self, parent,
                 duree_ms: int = 2800,
                 callback=None):
        super().__init__(parent)
        self._callback  = callback
        self._duree_ms  = duree_ms
        self._alpha     = 0.0
        self._phase     = "in"  # in → hold → out

        # Fenêtre sans bordure, centrée
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#0A1628")
        self.resizable(False, False)

        w, h = 520, 340
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._construire()
        self._animer_entree()

    def _construire(self):
        # Fond principal
        frame = ctk.CTkFrame(
            self, fg_color="#0A1628",
            corner_radius=16,
            border_width=2,
            border_color="#2563EB")
        frame.pack(fill="both", expand=True,
                   padx=2, pady=2)

        # Drapeau algérien (texte Unicode large)
        ctk.CTkLabel(
            frame, text="🇩🇿",
            font=("Segoe UI", 80)
        ).pack(pady=(30, 4))

        # Ligne verte/blanche simulée
        f_flag = ctk.CTkFrame(
            frame, fg_color="transparent")
        f_flag.pack()
        ctk.CTkFrame(
            f_flag, width=60, height=6,
            fg_color="#006233",
            corner_radius=3
        ).pack(side="left", padx=2)
        ctk.CTkFrame(
            f_flag, width=60, height=6,
            fg_color="#FFFFFF",
            corner_radius=3
        ).pack(side="left", padx=2)

        # Titre
        ctk.CTkLabel(
            frame,
            text="EPSP ES-SENIA",
            font=("Segoe UI", 22, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            frame,
            text="الجمهورية الجزائرية الديمقراطية الشعبية",
            font=("Segoe UI", 11),
            text_color="#94A3B8"
        ).pack()

        ctk.CTkLabel(
            frame,
            text="Gestionnaire de Reliquats de Congé Annuel",
            font=("Segoe UI", 10),
            text_color="#64748B"
        ).pack(pady=(2, 10))

        # Barre de progression
        self.barre = ctk.CTkProgressBar(
            frame,
            mode="determinate",
            fg_color="#1E3A5F",
            progress_color="#2563EB",
            height=4,
            corner_radius=2)
        self.barre.pack(
            fill="x", padx=40, pady=(4, 8))
        self.barre.set(0)

        # Version
        self.lbl_status = ctk.CTkLabel(
            frame,
            text=f"Chargement…  {get_full_label()}",
            font=("Segoe UI", 9),
            text_color="#475569")
        self.lbl_status.pack()

        ctk.CTkLabel(
            frame,
            text="COPYRIGHT ILINE TECH 2026 "
                 "BY FERAK ALADDIN",
            font=("Segoe UI", 8),
            text_color="#1E3A5F"
        ).pack(pady=(8, 0))

    def _animer_entree(self):
        """Fade-in progressif."""
        if self._alpha < 1.0:
            self._alpha = min(1.0, self._alpha + 0.08)
            self.attributes("-alpha", self._alpha)
            self.after(16, self._animer_entree)
        else:
            self._animer_progression()

    def _animer_progression(self, val=0.0):
        """Barre de progression."""
        if val <= 1.0:
            self.barre.set(val)
            pct = int(val * 100)
            msgs = {
                0:  "Initialisation…",
                25: "Chargement base de données…",
                50: "Vérification intégrité…",
                75: "Préparation interface…",
                90: "Presque prêt…",
                100:"Bienvenue !"
            }
            for seuil in sorted(msgs.keys(),
                                reverse=True):
                if pct >= seuil:
                    self.lbl_status.configure(
                        text=f"{msgs[seuil]}  "
                             f"{get_full_label()}")
                    break
            self.after(
                18,
                lambda: self._animer_progression(
                    val + 0.012))
        else:
            self.after(400, self._animer_sortie)

    def _animer_sortie(self, alpha=1.0):
        """Fade-out progressif."""
        if alpha > 0.0:
            alpha = max(0.0, alpha - 0.08)
            self.attributes("-alpha", alpha)
            self.after(
                16,
                lambda: self._animer_sortie(alpha))
        else:
            self.destroy()
            if self._callback:
                self._callback()
