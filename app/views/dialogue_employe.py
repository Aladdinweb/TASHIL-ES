# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Ajout / Modification d'un employé — EPSP ES-SENIA
Inclut : Polyclinique, Grade complet, Soldes initiaux.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import employes_dao
from app.utils.polycliniques_dao import lister_polycliniques
from app.utils.database import get_connection

GRADES = [
    # Corps médical
    "Médecin",
    "Médecin Spécialiste",
    "Chirurgien Dentiste",
    "Pharmacien",
    "Biologiste",
    "Psychologue",
    # Paramédical
    "Manipulateur Radio",
    "Infirmier Anesthésiste",
    "Infirmière",
    "Infirmier",
    "Sage-Femme",
    "Puéricultrice",
    "Aide-Puéricultrice",
    "ATS (Agent Technique de Santé)",
    "Laborantine",
    "Préparatrice en Pharmacie",
    "Opticien",
    "Assistante Médicale",
    "Assistante Sociale",
    "Aide Soignant",
    # Administration
    "Administrateur (ADM)",
    "Agent de Bureau",
    # OP
    "Agent de Sécurité (OP)",
    "Ambulancier (OP)",
    "Femme de Ménage (OP)",
    # Autre
    "Autre",
]


class DialogueEmploye(DialogueBase):
    def __init__(self, parent, emp_id=None,
                 callback_succes=None):
        self._emp_id   = emp_id
        self._callback = callback_succes
        self._donnees  = (employes_dao.obtenir_employe(emp_id)
                          if emp_id else None)
        self._depts    = employes_dao.lister_departements()
        self._polys    = lister_polycliniques()

        titre = ("Modifier l'employé" if emp_id
                 else "＋  Nouvel employé")
        super().__init__(parent, titre=titre,
                         largeur=580, hauteur=700)

    def _construire_corps(self):
        pad  = 20
        cors = self.frame_corps

        # ── helpers ──────────────────────────────────────────
        def sep(texte):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(16, 4))
            ctk.CTkLabel(f, text=texte,
                         font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(
                             side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                         side="left", fill="x",
                         expand=True, padx=(8, 0))

        def champ(label, placeholder="", obligatoire=False):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(
                f, text=label + ("  *" if obligatoire else ""),
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w")
            e = ctk.CTkEntry(
                f, placeholder_text=placeholder,
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"], height=38,
                corner_radius=DIMENSIONS["rayon_bouton"])
            e.pack(fill="x", pady=(4, 0))
            return e

        def menu(label, valeurs, obligatoire=False):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(
                f, text=label + ("  *" if obligatoire else ""),
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w")
            m = ctk.CTkOptionMenu(
                f, values=valeurs,
                fg_color=COULEURS["bg_champ"],
                button_color=COULEURS["accent_bleu"],
                button_hover_color=COULEURS["accent_bleu_clair"],
                dropdown_fg_color=COULEURS["bg_carte"],
                dropdown_hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                dropdown_text_color=COULEURS["texte_principal"],
                font=POLICES["corps"],
                dropdown_font=POLICES["corps"],
                corner_radius=DIMENSIONS["rayon_bouton"],
                height=38)
            m.pack(fill="x", pady=(4, 0))
            return m

        # ── Section 1 : Identification ────────────────────────
        sep("Identification")
        self.e_matricule = champ(
            "Matricule", "Ex : MR-001", True)
        self.e_nom       = champ(
            "Nom", "Ex : BENSALEM", True)
        self.e_prenom    = champ(
            "Prénom", "Ex : Kamel", True)

        # ── Section 2 : Affectation ───────────────────────────
        sep("Affectation")

        # Polyclinique (NOUVEAU — champ principal)
        f_poly = ctk.CTkFrame(cors, fg_color="transparent")
        f_poly.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(f_poly,
                     text="Polyclinique  *",
                     font=POLICES["corps_bold"],
                     text_color=COULEURS["texte_secondaire"]).pack(
                         anchor="w")
        noms_polys = (["— Sélectionner une polyclinique —"] +
                      [p["nom"] for p in self._polys])
        self.m_poly = ctk.CTkOptionMenu(
            f_poly, values=noms_polys,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            dropdown_font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=38)
        self.m_poly.pack(fill="x", pady=(4, 0))

        # Département
        noms_depts = [f"{d['code']} — {d['nom']}"
                      for d in self._depts]
        self.m_dept = menu(
            "Service / Département", noms_depts, True)

        # ── Section 3 : Grade & Poste ─────────────────────────
        sep("Grade & Poste")
        self.m_grade = menu("Grade / Corps", GRADES, True)
        self.e_poste = champ(
            "Poste occupé",
            "Ex : Manipulateur Principal")

        # ── Section 4 : Options ───────────────────────────────
        sep("Options")

        f_radio = ctk.CTkFrame(cors, fg_color="transparent")
        f_radio.pack(fill="x", padx=pad, pady=(0, 10))
        self.var_radio = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            f_radio,
            text="Bénéficiaire protection radiation (MANIP-RADIO)",
            variable=self.var_radio,
            font=POLICES["corps"],
            text_color=COULEURS["texte_principal"],
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            checkmark_color="#FFFFFF",
            border_color=COULEURS["bordure"]
        ).pack(anchor="w")

        if self._emp_id:
            f_actif = ctk.CTkFrame(cors, fg_color="transparent")
            f_actif.pack(fill="x", padx=pad, pady=(0, 10))
            self.var_actif = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                f_actif, text="Employé actif",
                variable=self.var_actif,
                font=POLICES["corps"],
                text_color=COULEURS["texte_principal"],
                fg_color=COULEURS["accent_vert"],
                hover_color="#059669",
                checkmark_color="#FFFFFF",
                border_color=COULEURS["bordure"]
            ).pack(anchor="w")

        # ── Section 5 : Soldes initiaux ───────────────────────
        if not self._emp_id:
            sep("Soldes de congé initiaux")

            ctk.CTkLabel(
                cors,
                text="Entrez les jours restants pour chaque année "
                     "(laisser 0 si aucun reliquat).",
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"],
                wraplength=500
            ).pack(anchor="w", padx=pad, pady=(0, 8))

            annee_courante = datetime.date.today().year
            self._soldes_champs = {}

            for annee in [annee_courante - 2,
                          annee_courante - 1,
                          annee_courante]:
                f_a = ctk.CTkFrame(cors, fg_color="transparent")
                f_a.pack(fill="x", padx=pad, pady=(0, 6))
                f_a.columnconfigure(0, weight=1)
                f_a.columnconfigure(1, weight=1)
                f_a.columnconfigure(2, weight=1)

                ctk.CTkLabel(
                    f_a,
                    text=f"Année {annee} :",
                    font=POLICES["corps_bold"],
                    text_color=(COULEURS["accent_orange"]
                                if annee < annee_courante
                                else COULEURS["accent_vert"]),
                    width=100, anchor="w"
                ).grid(row=0, column=0, sticky="w")

                ctk.CTkLabel(
                    f_a, text="Initiaux :",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).grid(row=0, column=1, sticky="e", padx=(0, 4))

                e_init = ctk.CTkEntry(
                    f_a, width=70,
                    fg_color=COULEURS["bg_champ"],
                    border_color=COULEURS["bordure"],
                    text_color=COULEURS["texte_principal"],
                    font=POLICES["corps"], height=32,
                    corner_radius=DIMENSIONS["rayon_bouton"])
                e_init.insert(0, "30")
                e_init.grid(row=0, column=2, sticky="w",
                            padx=(0, 8))

                ctk.CTkLabel(
                    f_a, text="Utilisés :",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).grid(row=0, column=3, sticky="e",
                       padx=(8, 4))

                e_util = ctk.CTkEntry(
                    f_a, width=70,
                    fg_color=COULEURS["bg_champ"],
                    border_color=COULEURS["bordure"],
                    text_color=COULEURS["texte_principal"],
                    font=POLICES["corps"], height=32,
                    corner_radius=DIMENSIONS["rayon_bouton"])
                e_util.insert(0, "0")
                e_util.grid(row=0, column=4, sticky="w")

                self._soldes_champs[annee] = (e_init, e_util)

            f_a.columnconfigure(3, weight=1)
            f_a.columnconfigure(4, weight=1)

        # Label erreur
        self._lbl_erreur = ctk.CTkLabel(
            cors, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)

        self.btn_valider.configure(
            text="Enregistrer l'employé")

        if self._donnees:
            self._preremplir()

    def _preremplir(self):
        d = self._donnees
        self.e_matricule.insert(0, d["matricule"])
        self.e_nom.insert(0, d["nom"])
        self.e_prenom.insert(0, d["prenom"])
        if d["grade"] in GRADES:
            self.m_grade.set(d["grade"])
        self.e_poste.insert(0, d.get("poste") or "")

        for dept in self._depts:
            if dept["id"] == d["departement_id"]:
                self.m_dept.set(
                    f"{dept['code']} — {dept['nom']}")
                break

        # Polyclinique
        poly_id = d.get("polyclinique_id")
        if poly_id:
            for p in self._polys:
                if p["id"] == poly_id:
                    self.m_poly.set(p["nom"])
                    break

        self.var_radio.set(bool(d.get("est_manip_radio")))
        if hasattr(self, "var_actif"):
            self.var_actif.set(bool(d.get("actif", 1)))

    def _valider(self):
        self._cacher_erreur()

        matricule = self.e_matricule.get().strip().upper()
        nom       = self.e_nom.get().strip().upper()
        prenom    = self.e_prenom.get().strip()
        grade     = self.m_grade.get()
        poste     = self.e_poste.get().strip()
        dept_sel  = self.m_dept.get()
        poly_sel  = self.m_poly.get()

        # Validations
        if not matricule:
            self._afficher_erreur("Le matricule est obligatoire.")
            return
        if not nom:
            self._afficher_erreur("Le nom est obligatoire.")
            return
        if not prenom:
            self._afficher_erreur("Le prénom est obligatoire.")
            return
        if (not poly_sel or
                poly_sel == "— Sélectionner une polyclinique —"):
            self._afficher_erreur(
                "Veuillez sélectionner une polyclinique.")
            return
        if not dept_sel or "—" not in dept_sel:
            self._afficher_erreur(
                "Veuillez sélectionner un département.")
            return
        if employes_dao.matricule_existe(
                matricule, exclure_id=self._emp_id):
            self._afficher_erreur(
                f"Matricule « {matricule} » déjà utilisé.")
            return

        # Résoudre dept_id
        code_dept = dept_sel.split("—")[0].strip()
        dept_id   = next(
            (d["id"] for d in self._depts
             if d["code"] == code_dept), None)
        if not dept_id:
            self._afficher_erreur("Département invalide.")
            return

        # Résoudre poly_id
        poly_id = next(
            (p["id"] for p in self._polys
             if p["nom"] == poly_sel), None)

        data = {
            "matricule":       matricule,
            "nom":             nom,
            "prenom":          prenom,
            "grade":           grade,
            "poste":           poste,
            "departement_id":  dept_id,
            "polyclinique_id": poly_id,
            "est_manip_radio": self.var_radio.get(),
            "actif": (self.var_actif.get()
                      if hasattr(self, "var_actif") else True),
        }

        try:
            if self._emp_id:
                employes_dao.modifier_employe(
                    self._emp_id, data)
                resultat = {"action": "modifie"}
            else:
                nouvel_id = self._creer_avec_soldes(data)
                resultat  = {"action": "cree",
                             "id": nouvel_id}

            if self._callback:
                self._callback(resultat)
            self.destroy()

        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")

    def _creer_avec_soldes(self, data: dict) -> int:
        """Crée l'employé puis ses soldes initiaux."""
        conn = get_connection()

        cur = conn.execute("""
            INSERT INTO employes
                (matricule, nom, prenom, grade, poste,
                 departement_id, polyclinique_id,
                 est_manip_radio, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            data["matricule"], data["nom"], data["prenom"],
            data["grade"], data["poste"],
            data["departement_id"], data.get("polyclinique_id"),
            1 if data.get("est_manip_radio") else 0,
        ))
        emp_id = cur.lastrowid

        # Insérer les soldes depuis les champs du formulaire
        if hasattr(self, "_soldes_champs"):
            for annee, (e_init, e_util) in \
                    self._soldes_champs.items():
                try:
                    initiaux  = float(
                        e_init.get().strip() or "30")
                    utilises  = float(
                        e_util.get().strip() or "0")
                    if initiaux < 0:
                        initiaux = 30
                    if utilises < 0:
                        utilises = 0
                except ValueError:
                    initiaux, utilises = 30.0, 0.0

                conn.execute("""
                    INSERT OR IGNORE INTO conges_annuels
                        (employe_id, annee,
                         jours_initiaux, jours_utilises)
                    VALUES (?, ?, ?, ?)
                """, (emp_id, annee, initiaux, utilises))
        else:
            # Fallback : solde année courante uniquement
            annee = datetime.date.today().year
            conn.execute("""
                INSERT OR IGNORE INTO conges_annuels
                    (employe_id, annee,
                     jours_initiaux, jours_utilises)
                VALUES (?, ?, 30, 0)
            """, (emp_id, annee))

        conn.commit()
        conn.close()
        return emp_id
