# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Splash Screen — Thread-safe, zéro deadlock.
"""
import customtkinter as ctk
from app.utils.version import get_full_label


class SplashScreen(ctk.CTkToplevel):
    """
    Splash animé. callback() appelé via after()
    — jamais depuis un thread secondaire.
    """

    def __init__(self, parent,
                 duree_ms: int = 2400,
                 callback=None):
        super().__init__(parent)
        self._callback = callback
        self._parent   = parent

        # Fenêtre sans décoration
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(fg_color="#0A1628")
        self.resizable(False, False)

        w, h = 500, 320
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._construire()
        # Démarrer animation via after()
        self.after(10, lambda: self._fade(0.0, "in"))

    def _construire(self):
        frame = ctk.CTkFrame(
            self, fg_color="#0A1628",
            corner_radius=14,
            border_width=2,
            border_color="#1E40AF")
        frame.pack(fill="both", expand=True,
                   padx=2, pady=2)

        ctk.CTkLabel(
            frame, text="🇩🇿",
            font=("Segoe UI", 70)
        ).pack(pady=(28, 2))

        ctk.CTkLabel(
            frame,
            text="الجمهورية الجزائرية الديمقراطية الشعبية",
            font=("Segoe UI", 12, "bold"),
            text_color="#E2E8F0"
        ).pack()

        ctk.CTkLabel(
            frame, text="وزارة الصحة",
            font=("Segoe UI", 11),
            text_color="#64748B"
        ).pack(pady=(2, 10))

        ctk.CTkLabel(
            frame,
            text="⚕  EPSP ES-SENIA",
            font=("Segoe UI", 18, "bold"),
            text_color="#3B82F6"
        ).pack()

        ctk.CTkLabel(
            frame,
            text="Gestionnaire de Reliquats "
                 "de Congé Annuel",
            font=("Segoe UI", 9),
            text_color="#475569"
        ).pack(pady=(2, 10))

        self.barre = ctk.CTkProgressBar(
            frame,
            mode="determinate",
            fg_color="#1E3A5F",
            progress_color="#2563EB",
            height=4, corner_radius=2)
        self.barre.pack(
            fill="x", padx=50, pady=(0, 6))
        self.barre.set(0)

        self.lbl_ver = ctk.CTkLabel(
            frame,
            text=get_full_label(),
            font=("Segoe UI", 9),
            text_color="#334155")
        self.lbl_ver.pack()

    def _fade(self, alpha: float, direction: str):
        """Fade in/out via after() — thread-safe."""
        if direction == "in":
            alpha = min(1.0, alpha + 0.07)
            self.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(
                    14,
                    lambda: self._fade(
                        alpha, "in"))
            else:
                # Démarrer progression barre
                self.after(
                    10,
                    lambda: self._progres(0.0))
        else:
            alpha = max(0.0, alpha - 0.07)
            self.attributes("-alpha", alpha)
            if alpha > 0.0:
                self.after(
                    14,
                    lambda: self._fade(
                        alpha, "out"))
            else:
                self._terminer()

    def _progres(self, val: float):
        """Progression barre via after()."""
        if val <= 1.0:
            self.barre.set(val)
            msgs = {
                0.0:  "Initialisation…",
                0.3:  "Chargement données…",
                0.6:  "Vérification intégrité…",
                0.85: "Préparation interface…",
                1.0:  "Bienvenue !",
            }
            for seuil in sorted(
                    msgs.keys(), reverse=True):
                if val >= seuil:
                    self.lbl_ver.configure(
                        text=f"{msgs[seuil]}  "
                             f"{get_full_label()}")
                    break
            self.after(
                20,
                lambda: self._progres(
                    round(val + 0.015, 3)))
        else:
            # Pause puis fade out
            self.after(
                300,
                lambda: self._fade(1.0, "out"))

    def _terminer(self):
        """Ferme le splash et appelle callback."""
        try:
            self.destroy()
        except Exception:
            pass
        if self._callback:
            # Callback via after sur le parent
            # — garantit thread principal
            try:
                self._parent.after(
                    10, self._callback)
            except Exception:
                pass
