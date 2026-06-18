# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Dialogue Employé — Version définitive
Corrections : Département correct, Grade→Poste dynamique,
Soldes 2022-2026, boutons Enregistrer/Annuler visibles.
"""
import datetime
import customtkinter as ctk
from app.utils.theme import COULEURS, POLICES, DIMENSIONS
from app.views.dialogue_base import DialogueBase
from app.utils import employes_dao
from app.utils.polycliniques_dao import lister_polycliniques
from app.utils.database import get_connection

# ── Groupes / Services opérationnels ─────────────────────────────
GROUPES = [
    "Groupe A",
    "Groupe B",
    "Groupe C",
    "Groupe D",
    "Garde Pôle",
    "Administration",
]

# ── Grades officiels EPSP ─────────────────────────────────────────
GRADES = [
    "Médecin",
    "Médecin Spécialiste",
    "Chirurgien Dentiste",
    "Pharmacien",
    "Biologiste",
    "Psychologue",
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
    "Administrateur (ADM)",
    "Agent de Bureau",
    "Agent de Sécurité (OP)",
    "Ambulancier (OP)",
    "Femme de Ménage (OP)",
    "Autre",
]

# ── Postes suggérés selon le grade ───────────────────────────────
POSTES_PAR_GRADE = {
    "Médecin": [
        "Généraliste",
        "Médecin des Urgences",
        "Médecin Spécialiste",
        "Médecin Chef de Service",
        "Médecin Inspecteur",
    ],
    "Médecin Spécialiste": [
        "Cardiologue",
        "Pneumologue",
        "Chirurgien",
        "Pédiatre",
        "Gynécologue",
        "Ophtalmologue",
        "Dermatologue",
        "Neurologue",
        "Autre Spécialiste",
    ],
    "Ambulancier (OP)": [
        "Conducteur de niveau 1",
        "Conducteur de niveau 2",
        "Conducteur Ambulancier Principal",
    ],
    "Agent de Sécurité (OP)": [
        "Agent de Sécurité",
        "Chef d'Équipe Sécurité",
        "Responsable Sécurité",
    ],
    "Infirmière": [
        "Infirmière de Soins",
        "Infirmière Principale",
        "Infirmière Chef",
        "Infirmière des Urgences",
        "Infirmière de Bloc",
    ],
    "Infirmier": [
        "Infirmier de Soins",
        "Infirmier Principal",
        "Infirmier Chef",
        "Infirmier des Urgences",
    ],
    "Manipulateur Radio": [
        "Manipulateur",
        "Manipulateur Principal",
        "Manipulateur Chef",
    ],
    "Pharmacien": [
        "Pharmacien Hospitalier",
        "Pharmacien Principal",
        "Pharmacien Chef",
    ],
    "Administrateur (ADM)": [
        "Responsable RH",
        "Responsable Administratif",
        "Secrétaire de Direction",
        "Agent Comptable",
    ],
    "Agent de Bureau": [
        "Secrétaire",
        "Agent d'Accueil",
        "Agent Administratif",
        "Archiviste",
    ],
    "Sage-Femme": [
        "Sage-Femme",
        "Sage-Femme Principale",
        "Sage-Femme Chef",
    ],
}
POSTES_DEFAUT = ["Poste principal", "Poste secondaire",
                  "Responsable", "Autre"]


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
                         largeur=600, hauteur=780)

    def _construire_corps(self):
        pad  = 20
        cors = self.frame_corps

        def sep(texte, couleur=None):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(16, 4))
            ctk.CTkLabel(
                f, text=texte,
                font=POLICES["sous_titre"],
                text_color=couleur or COULEURS["accent_bleu"]
            ).pack(side="left")
            ctk.CTkFrame(
                f, height=1,
                fg_color=couleur or COULEURS["bordure_active"]
            ).pack(side="left", fill="x",
                   expand=True, padx=(8, 0))

        def champ(label, placeholder="",
                  obligatoire=False):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(
                f,
                text=label + ("  *" if obligatoire else ""),
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

        def menu_opt(label, valeurs, obligatoire=False,
                     commande=None):
            f = ctk.CTkFrame(cors, fg_color="transparent")
            f.pack(fill="x", padx=pad, pady=(0, 10))
            ctk.CTkLabel(
                f,
                text=label + ("  *" if obligatoire else ""),
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
                height=38,
                command=commande)
            m.pack(fill="x", pady=(4, 0))
            return m

        # ══════════════════════════════════════════════════
        # SECTION 1 — Identification
        # ══════════════════════════════════════════════════
        sep("① Identification")

        self.e_nom      = champ("Nom", "Ex : BENSALEM",
                                True)
        self.e_prenom   = champ("Prénom", "Ex : Kamel",
                                True)
        self.e_matricule = champ(
            "Matricule (رقم التسجيل)",
            "Ex : MR-001", True)

        # Année d'entrée
        f_annee = ctk.CTkFrame(cors, fg_color="transparent")
        f_annee.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(
            f_annee,
            text="Année d'entrée (سنة الدخول)",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        annee_cour = datetime.date.today().year
        annees_ent = [str(y) for y in range(
            annee_cour, annee_cour - 40, -1)]
        self.m_annee_ent = ctk.CTkOptionMenu(
            f_annee, values=annees_ent,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=38)
        self.m_annee_ent.pack(fill="x", pady=(4, 0))

        # ══════════════════════════════════════════════════
        # SECTION 2 — Affectation
        # ══════════════════════════════════════════════════
        sep("② Affectation")

        # Polyclinique
        f_poly = ctk.CTkFrame(cors, fg_color="transparent")
        f_poly.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(
            f_poly,
            text="Polyclinique  *",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        noms_polys = (
            ["— Sélectionner une polyclinique —"] +
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

        # Service / Département — CORRIGÉ
        f_dept = ctk.CTkFrame(cors, fg_color="transparent")
        f_dept.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(
            f_dept,
            text="Service / Groupe  *",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        self.m_groupe = ctk.CTkOptionMenu(
            f_dept, values=GROUPES,
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
        self.m_groupe.pack(fill="x", pady=(4, 0))
        self.m_groupe.set(GROUPES[0])

        # Département DB (caché mais requis)
        self._dept_id_cache = (
            self._depts[0]["id"]
            if self._depts else 1)

        # ══════════════════════════════════════════════════
        # SECTION 3 — Grade & Poste dynamique
        # ══════════════════════════════════════════════════
        sep("③ Grade & Poste (التخصص / الرتبة)")

        # Grade
        f_grade = ctk.CTkFrame(cors,
                               fg_color="transparent")
        f_grade.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(
            f_grade, text="Grade / Corps  *",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        self.m_grade = ctk.CTkOptionMenu(
            f_grade, values=GRADES,
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
            height=38,
            command=self._on_grade_change)
        self.m_grade.pack(fill="x", pady=(4, 0))

        # Poste occupé — dynamique selon grade
        f_poste = ctk.CTkFrame(cors,
                               fg_color="transparent")
        f_poste.pack(fill="x", padx=pad, pady=(0, 10))
        ctk.CTkLabel(
            f_poste, text="Poste occupé",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")

        # Frame contenant soit le menu soit le champ texte
        self.frame_poste_widget = ctk.CTkFrame(
            f_poste, fg_color="transparent")
        self.frame_poste_widget.pack(
            fill="x", pady=(4, 0))

        self.m_poste = ctk.CTkOptionMenu(
            self.frame_poste_widget,
            values=POSTES_DEFAUT,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=38)
        self.m_poste.pack(fill="x")

        self.e_poste_libre = ctk.CTkEntry(
            self.frame_poste_widget,
            placeholder_text=(
                "Ex : Conducteur de niveau 1"),
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=38,
            corner_radius=DIMENSIONS["rayon_bouton"])
        # Masqué par défaut
        self.e_poste_libre.pack(fill="x")
        self.e_poste_libre.pack_forget()
        self._poste_mode = "menu"

        # Déclencher une fois pour init
        self._on_grade_change(GRADES[0])

        # ══════════════════════════════════════════════════
        # SECTION 4 — Soldes initiaux (2022 → N+1)
        # ══════════════════════════════════════════════════
        if not self._emp_id:
            sep("④ Soldes de congé initiaux",
                couleur=COULEURS["accent_vert"])

            ctk.CTkLabel(
                cors,
                text="Renseignez les reliquats historiques "
                     "pour chaque année (0 si aucun).",
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"],
                wraplength=520
            ).pack(anchor="w", padx=pad,
                   pady=(0, 8))

            annee_cour = datetime.date.today().year
            # Années de 2022 jusqu'à année courante
            annees_soldes = list(range(2022, annee_cour + 1))
            self._soldes_champs = {}

            for annee in annees_soldes:
                is_old = annee < annee_cour
                coul_a = (COULEURS["accent_orange"]
                          if is_old
                          else COULEURS["accent_vert"])

                f_a = ctk.CTkFrame(
                    cors,
                    fg_color=COULEURS["bg_carte"],
                    corner_radius=6)
                f_a.pack(fill="x", padx=pad,
                         pady=(0, 6))

                f_head = ctk.CTkFrame(
                    f_a, fg_color="transparent")
                f_head.pack(fill="x", padx=10,
                            pady=(6, 4))

                tag = " 🔴 Reliquat" if is_old else " ✅ En cours"
                ctk.CTkLabel(
                    f_head,
                    text=f"Année {annee}{tag}",
                    font=POLICES["corps_bold"],
                    text_color=coul_a
                ).pack(side="left")

                f_fields = ctk.CTkFrame(
                    f_a, fg_color="transparent")
                f_fields.pack(fill="x", padx=10,
                              pady=(0, 8))

                # Initiaux
                ctk.CTkLabel(
                    f_fields,
                    text="Jours initiaux :",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(side="left")
                e_init = ctk.CTkEntry(
                    f_fields, width=65,
                    fg_color=COULEURS["bg_champ"],
                    border_color=COULEURS["bordure"],
                    text_color=COULEURS["texte_principal"],
                    font=POLICES["corps"], height=32,
                    corner_radius=DIMENSIONS["rayon_bouton"])
                e_init.insert(0, "30")
                e_init.pack(side="left",
                            padx=(4, 16))

                # Utilisés
                ctk.CTkLabel(
                    f_fields,
                    text="Jours utilisés :",
                    font=POLICES["petit"],
                    text_color=COULEURS["texte_secondaire"]
                ).pack(side="left")
                e_util = ctk.CTkEntry(
                    f_fields, width=65,
                    fg_color=COULEURS["bg_champ"],
                    border_color=COULEURS["bordure"],
                    text_color=COULEURS["texte_principal"],
                    font=POLICES["corps"], height=32,
                    corner_radius=DIMENSIONS["rayon_bouton"])
                e_util.insert(0, "0")
                e_util.pack(side="left", padx=(4, 0))

                self._soldes_champs[annee] = (e_init, e_util)

        # Label erreur
        self._lbl_erreur = ctk.CTkLabel(
            cors, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)
        self._lbl_erreur.pack(fill="x", padx=pad,
                              pady=(8, 4))

        # Bouton valider
        self.btn_valider.configure(
            text="💾  Enregistrer l'employé")

        if self._donnees:
            self._preremplir()

    # ── Dynamisme Grade → Poste ───────────────────────────
    def _on_grade_change(self, grade: str):
        postes = POSTES_PAR_GRADE.get(grade)

        for w in self.frame_poste_widget.winfo_children():
            w.pack_forget()

        if postes:
            # Afficher le menu déroulant
            self.m_poste.configure(values=postes)
            self.m_poste.set(postes[0])
            self.m_poste.pack(fill="x")
            self._poste_mode = "menu"
        else:
            # Afficher le champ texte libre
            self.e_poste_libre.pack(fill="x")
            self._poste_mode = "libre"

    def _get_poste(self) -> str:
        if self._poste_mode == "menu":
            return self.m_poste.get()
        else:
            return self.e_poste_libre.get().strip()

    # ── Pré-remplissage (modification) ───────────────────
    def _preremplir(self):
        d = self._donnees
        self.e_nom.insert(0, d["nom"])
        self.e_prenom.insert(0, d["prenom"])
        self.e_matricule.insert(0, d["matricule"])

        if d.get("annee_entree"):
            self.m_annee_ent.set(str(d["annee_entree"]))

        # Polyclinique
        for p in self._polys:
            if p["id"] == d.get("polyclinique_id"):
                self.m_poly.set(p["nom"])
                break

        # Grade
        if d.get("grade") in GRADES:
            self.m_grade.set(d["grade"])
            self._on_grade_change(d["grade"])

        # Poste
        poste = d.get("poste") or ""
        if self._poste_mode == "menu":
            postes = POSTES_PAR_GRADE.get(
                d.get("grade", ""), [])
            if poste in postes:
                self.m_poste.set(poste)
            elif postes:
                self.m_poste.set(postes[0])
        else:
            self.e_poste_libre.insert(0, poste)

    # ── Validation & Enregistrement ───────────────────────
    def _valider(self):
        self._cacher_erreur()

        nom       = self.e_nom.get().strip().upper()
        prenom    = self.e_prenom.get().strip()
        matricule = self.e_matricule.get().strip().upper()
        grade     = self.m_grade.get()
        poste     = self._get_poste()
        poly_sel  = self.m_poly.get()
        groupe    = self.m_groupe.get()

        try:
            annee_ent = int(self.m_annee_ent.get())
        except ValueError:
            annee_ent = None

        # Validations
        if not nom:
            self._afficher_erreur("Le nom est obligatoire.")
            return
        if not prenom:
            self._afficher_erreur(
                "Le prénom est obligatoire.")
            return
        if not matricule:
            self._afficher_erreur(
                "Le matricule est obligatoire.")
            return
        if (not poly_sel or
                "Sélectionner" in poly_sel):
            self._afficher_erreur(
                "Veuillez sélectionner une polyclinique.")
            return
        if employes_dao.matricule_existe(
                matricule, exclure_id=self._emp_id):
            self._afficher_erreur(
                f"Matricule « {matricule} » déjà utilisé.")
            return

        # Résoudre polyclinique
        poly_id = next(
            (p["id"] for p in self._polys
             if p["nom"] == poly_sel), None)

        # Résoudre département DB
        # On mappe le groupe au premier département dispo
        dept_id = self._resoudre_dept(groupe)

        data = {
            "matricule":       matricule,
            "nom":             nom,
            "prenom":          prenom,
            "grade":           grade,
            "poste":           poste,
            "groupe":          groupe,
            "departement_id":  dept_id,
            "polyclinique_id": poly_id,
            "annee_entree":    annee_ent,
            "est_manip_radio": (
                1 if "Radio" in grade else 0),
            "actif": (self.var_actif.get()
                      if hasattr(self, "var_actif")
                      else True),
        }

        try:
            if self._emp_id:
                employes_dao.modifier_employe(
                    self._emp_id, data)
                res = {"action": "modifie"}
            else:
                nid = self._creer_avec_soldes(data)
                res = {"action": "cree", "id": nid}

            if self._callback:
                self._callback(res)
            self.destroy()

        except Exception as ex:
            self._afficher_erreur(f"Erreur : {str(ex)}")

    def _resoudre_dept(self, groupe: str) -> int:
        """
        Mappe le groupe opérationnel au département DB.
        Crée le département si nécessaire.
        """
        conn = get_connection()
        row = conn.execute(
            "SELECT id FROM departements WHERE code = ?",
            (groupe[:10].upper().replace(" ", "_"),)
        ).fetchone()

        if row:
            conn.close()
            return row["id"]

        # Créer le département à la volée
        cur = conn.execute("""
            INSERT OR IGNORE INTO departements
                (code, nom, description)
            VALUES (?, ?, ?)
        """, (
            groupe[:10].upper().replace(" ", "_"),
            groupe,
            f"Groupe opérationnel : {groupe}"
        ))
        conn.commit()
        dept_id = cur.lastrowid or conn.execute(
            "SELECT id FROM departements WHERE code=?",
            (groupe[:10].upper().replace(" ", "_"),)
        ).fetchone()["id"]
        conn.close()
        return dept_id

    def _creer_avec_soldes(self, data: dict) -> int:
        conn = get_connection()
        cur = conn.execute("""
            INSERT INTO employes
                (matricule, nom, prenom, grade, poste,
                 departement_id, polyclinique_id,
                 est_manip_radio, annee_entree, actif)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            data["matricule"], data["nom"],
            data["prenom"], data["grade"],
            data["poste"], data["departement_id"],
            data.get("polyclinique_id"),
            data.get("est_manip_radio", 0),
            data.get("annee_entree"),
        ))
        emp_id = cur.lastrowid

        if hasattr(self, "_soldes_champs"):
            for annee, (e_init, e_util) in \
                    self._soldes_champs.items():
                try:
                    init = float(
                        e_init.get().strip() or "30")
                    util = float(
                        e_util.get().strip() or "0")
                    init = max(0.0, init)
                    util = max(0.0, min(util, init))
                except ValueError:
                    init, util = 30.0, 0.0

                # Ne créer que si initiaux > 0
                if init > 0:
                    conn.execute("""
                        INSERT OR IGNORE INTO conges_annuels
                            (employe_id, annee,
                             jours_initiaux,
                             jours_utilises)
                        VALUES (?, ?, ?, ?)
                    """, (emp_id, annee, init, util))
        else:
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
