# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue : Ajout / Modification d'un employé — EPSP ES-SENIA
"""
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import employes_dao

# ── Grades officiels EPSP ES-SENIA ────────────────────────────────
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
    # OP — Ouvriers Professionnels
    "Agent de Sécurité (OP)",
    "Ambulancier (OP)",
    "Femme de Ménage (OP)",
    # Autre
    "Autre",
]


class DialogueEmploye(DialogueBase):
    def __init__(self, parent, emp_id: int = None,
                 callback_succes=None):
        self._emp_id = emp_id
        self._callback = callback_succes
        self._donnees_emp = (employes_dao.obtenir_employe(emp_id)
                             if emp_id else None)
        self._depts = employes_dao.lister_departements()
        titre = "Modifier l'employé" if emp_id else "Nouvel employé"
        super().__init__(parent, titre=titre,
                         largeur=560, hauteur=620)

    def _construire_corps(self):
        pad = 20
        corps = self.frame_corps

        def sep(texte):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(16, 4))
            ctk.CTkLabel(f, text=texte, font=POLICES["sous_titre"],
                         text_color=COULEURS["accent_bleu"]).pack(side="left")
            ctk.CTkFrame(f, height=1,
                         fg_color=COULEURS["bordure_active"]).pack(
                             side="left", fill="x", expand=True, padx=(8, 0))

        def champ(label, placeholder="", obligatoire=False):
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(f, text=label + ("  *" if obligatoire else ""),
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
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
            f = ctk.CTkFrame(corps, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(f, text=label + ("  *" if obligatoire else ""),
                         font=POLICES["corps_bold"],
                         text_color=COULEURS["texte_secondaire"]).pack(anchor="w")
            m = ctk.CTkOptionMenu(
                f, values=valeurs,
                fg_color=COULEURS["bg_champ"],
                button_color=COULEURS["accent_bleu"],
                button_hover_color=COULEURS["accent_bleu_clair"],
                dropdown_fg_color=COULEURS["bg_carte"],
                dropdown_hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_principal"],
                dropdown_text_color=COULEURS["texte_principal"],
                font=POLICES["corps"], dropdown_font=POLICES["corps"],
                corner_radius=DIMENSIONS["rayon_bouton"], height=38)
            m.pack(fill="x", pady=(4, 0))
            return m

        sep("Identification")
        self.e_matricule = champ("Matricule", "Ex : MR-004", True)
        self.e_nom       = champ("Nom", "Ex : BENSALEM", True)
        self.e_prenom    = champ("Prénom", "Ex : Kamel", True)

        sep("Poste & Département")
        self.m_grade = menu("Grade / Corps", GRADES, True)
        self.e_poste = champ("Poste occupé", "Ex : Manipulateur Principal")
        noms_depts = [f"{d['code']} — {d['nom']}" for d in self._depts]
        self.m_dept  = menu("Département", noms_depts, True)

        sep("Options")
        f_radio = ctk.CTkFrame(corps, fg_color="transparent")
        f_radio.pack(fill="x", padx=pad, pady=(0, 10))
        self.var_radio = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            f_radio,
            text="Bénéficiaire protection radiation (MANIP-RADIO)",
            variable=self.var_radio, font=POLICES["corps"],
            text_color=COULEURS["texte_principal"],
            fg_color=COULEURS["accent_bleu"],
            hover_color=COULEURS["accent_bleu_clair"],
            checkmark_color="#FFFFFF",
            border_color=COULEURS["bordure"]).pack(anchor="w")

        if self._emp_id:
            f_actif = ctk.CTkFrame(corps, fg_color="transparent")
            f_actif.pack(fill="x", padx=pad, pady=(0, 10))
            self.var_actif = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                f_actif, text="Employé actif",
                variable=self.var_actif, font=POLICES["corps"],
                text_color=COULEURS["texte_principal"],
                fg_color=COULEURS["accent_vert"],
                hover_color="#059669",
                checkmark_color="#FFFFFF",
                border_color=COULEURS["bordure"]).pack(anchor="w")

        self._lbl_erreur = ctk.CTkLabel(
            corps, text="", font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)

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
        for dept in self._depts:
            if dept["id"] == d["departement_id"]:
                self.m_dept.set(f"{dept['code']} — {dept['nom']}")
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

        if not matricule:
            self._afficher_erreur("Le matricule est obligatoire."); return
        if not nom:
            self._afficher_erreur("Le nom est obligatoire."); return
        if not prenom:
            self._afficher_erreur("Le prénom est obligatoire."); return
        if not dept_sel or "—" not in dept_sel:
            self._afficher_erreur("Veuillez sélectionner un département."); return
        if employes_dao.matricule_existe(matricule, exclure_id=self._emp_id):
            self._afficher_erreur(f"Matricule « {matricule} » déjà utilisé."); return

        code_dept = dept_sel.split("—")[0].strip()
        dept_id = next((d["id"] for d in self._depts
                        if d["code"] == code_dept), None)
        if not dept_id:
            self._afficher_erreur("Département invalide."); return

        data = {
            "matricule":      matricule,
            "nom":            nom,
            "prenom":         prenom,
            "grade":          grade,
            "poste":          poste,
            "departement_id": dept_id,
            "est_manip_radio":self.var_radio.get(),
            "actif":          (self.var_actif.get()
                               if hasattr(self, "var_actif") else True),
        }
        try:
            if self._emp_id:
                employes_dao.modifier_employe(self._emp_id, data)
                self.resultat = {"action": "modifie", "data": data}
            else:
                nouvel_id = employes_dao.creer_employe(data)
                self.resultat = {"action": "cree", "id": nouvel_id, "data": data}
            if self._callback:
                self._callback(self.resultat)
            self.destroy()
        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")
