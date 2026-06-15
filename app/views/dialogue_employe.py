# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Ajout / Modification d'un employé — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import employes_dao


# Grades officiels EPSP
GRADES = [
    "Médecin",
    "Médecin Spécialiste",
    "Chirurgien Dentiste",
    "Pharmacien",
    "Manipulateur Radio",
    "Infirmier Anesthésiste",
    "Infirmière",
    "Infirmier",
    "Aide Soignant",
    "Technicien Supérieur",
    "Technicien de Santé",
    "Agent Administratif",
    "Administrateur",
    "Autre",
]


class DialogueEmploye(DialogueBase):
    """
    Formulaire modal pour créer ou modifier un employé.
    - emp_id=None  → mode création
    - emp_id=<int> → mode modification (pré-remplissage)
    """

    def __init__(self, parent, emp_id: int = None,
                 callback_succes=None):
        self._emp_id = emp_id
        self._callback = callback_succes
        self._donnees_emp = (employes_dao.obtenir_employe(emp_id)
                             if emp_id else None)
        self._depts = employes_dao.lister_departements()

        titre = ("Modifier l'employé" if emp_id
                 else "Nouvel employé")
        super().__init__(parent, titre=titre,
                         largeur=560, hauteur=600)

    def _construire_corps(self):
        pad = 20
        corps = self.frame_corps

        def separateur_section(texte):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(16, 4))
            ctk.CTkLabel(f, text=texte,
                         font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                             side="left", fill="x", expand=True, padx=(8, 0))

        def champ(label, placeholder="", obligatoire=False):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            txt = label + ("  *" if obligatoire else "")
            ctk.CTkLabel(f, text=txt,
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w")
            e = ctk.CTkEntry(
                f,
                placeholder_text=placeholder,
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"],
                height=38,
                corner_radius=DIMENSIONS["rayon_bouton"]
            )
            e.pack(fill="x", pady=(4, 0))
            return e

        def menu(label, valeurs, obligatoire=False):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            txt = label + ("  *" if obligatoire else "")
            ctk.CTkLabel(f, text=txt,
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(
                             anchor="w")
            m = ctk.CTkOptionMenu(
                f,
                values=valeurs,
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
                height=38
            )
            m.pack(fill="x", pady=(4, 0))
            return m

        # ── Section 1 : Identification ──────────────────────────
        separateur_section("Identification")

        self.e_matricule = champ(
            "Matricule", "Ex : MR-004", obligatoire=True)
        self.e_nom       = champ("Nom", "Ex : BENSALEM", obligatoire=True)
        self.e_prenom    = champ("Prénom", "Ex : Kamel", obligatoire=True)

        # ── Section 2 : Poste & Département ────────────────────
        separateur_section("Poste & Département")

        self.m_grade = menu("Grade / Corps", GRADES, obligatoire=True)
        self.e_poste = champ("Poste occupé", "Ex : Manipulateur Principal")

        # Département
        noms_depts = [f"{d['code']} — {d['nom']}" for d in self._depts]
        self.m_dept = menu("Département  *", noms_depts)

        # ── Section 3 : Options ─────────────────────────────────
        separateur_section("Options")

        # Case Manip Radio
        frame_radio = ctk.CTkFrame(corps, fg_color="transparent")
        frame_radio.pack(fill="x", padx=pad, pady=(0, 10))
        self.var_radio = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame_radio,
            text="Bénéficiaire de la protection radiation (MANIP-RADIO)",
            variable=self.var_radio,
            font=POLICES["corps"],
            text_color=COULEURS["texte_principal"],
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            checkmark_color="#FFFFFF",
            border_color=COULEURS["bordure"],
        ).pack(anchor="w")

        # Case Actif (uniquement en modification)
        if self._emp_id:
            frame_actif = ctk.CTkFrame(corps, fg_color="transparent")
            frame_actif.pack(fill="x", padx=pad, pady=(0, 10))
            self.var_actif = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                frame_actif,
                text="Employé actif",
                variable=self.var_actif,
                font=POLICES["corps"],
                text_color=COULEURS["texte_principal"],
                fg_color=COULEURS["accent_vert"],
                hover_color="#059669",
                checkmark_color="#FFFFFF",
                border_color=COULEURS["bordure"],
            ).pack(anchor="w")

        # Label erreur (caché par défaut)
        self._lbl_erreur = ctk.CTkLabel(
            corps, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515",
            corner_radius=6
        )

        # Pré-remplissage si modification
        if self._donnees_emp:
            self._preremplir()

    def _preremplir(self):
        d = self._donnees_emp
        self.e_matricule.insert(0, d["matricule"])
        self.e_nom.insert(0, d["nom"])
        self.e_prenom.insert(0, d["prenom"])

        if d["grade"] in GRADES:
            self.m_grade.set(d["grade"])
        self.e_poste.insert(0, d.get("poste") or "")

        # Sélectionner le département
        for i, dept in enumerate(self._depts):
            if dept["id"] == d["departement_id"]:
                self.m_dept.set(
                    f"{dept['code']} — {dept['nom']}"
                )
                break

        self.var_radio.set(bool(d.get("est_manip_radio")))
        if hasattr(self, "var_actif"):
            self.var_actif.set(bool(d.get("actif", 1)))

    def _valider(self):
        self._cacher_erreur()

        # ── Récupérer les valeurs ─────────────────────────────
        matricule = self.e_matricule.get().strip().upper()
        nom       = self.e_nom.get().strip().upper()
        prenom    = self.e_prenom.get().strip()
        grade     = self.m_grade.get()
        poste     = self.e_poste.get().strip()
        dept_sel  = self.m_dept.get()

        # ── Validation ────────────────────────────────────────
        if not matricule:
            self._afficher_erreur("Le matricule est obligatoire.")
            return
        if not nom:
            self._afficher_erreur("Le nom est obligatoire.")
            return
        if not prenom:
            self._afficher_erreur("Le prénom est obligatoire.")
            return
        if not dept_sel or "—" not in dept_sel:
            self._afficher_erreur("Veuillez sélectionner un département.")
            return

        # Unicité du matricule
        if employes_dao.matricule_existe(matricule,
                                         exclure_id=self._emp_id):
            self._afficher_erreur(
                f"Le matricule « {matricule} » est déjà utilisé.")
            return

        # Résoudre l'ID département
        code_dept = dept_sel.split("—")[0].strip()
        dept_id = None
        for d in self._depts:
            if d["code"] == code_dept:
                dept_id = d["id"]
                break
        if not dept_id:
            self._afficher_erreur("Département invalide.")
            return

        # ── Construire le dictionnaire de données ─────────────
        data = {
            "matricule":       matricule,
            "nom":             nom,
            "prenom":          prenom,
            "grade":           grade,
            "poste":           poste,
            "departement_id":  dept_id,
            "est_manip_radio": self.var_radio.get(),
            "actif":           (self.var_actif.get()
                                if hasattr(self, "var_actif") else True),
        }

        # ── Enregistrement ────────────────────────────────────
        try:
            if self._emp_id:
                employes_dao.modifier_employe(self._emp_id, data)
                self.resultat = {"action": "modifie", "data": data}
            else:
                nouvel_id = employes_dao.creer_employe(data)
                self.resultat = {"action": "cree", "id": nouvel_id,
                                 "data": data}

            if self._callback:
                self._callback(self.resultat)
            self.destroy()

        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")
