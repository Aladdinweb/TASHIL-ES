# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Formulaire Employé — Validation assouplie
Obligatoires : Nom, Prénom, Grade, Polyclinique
Soldes : saisie du nombre restant uniquement
"""
import datetime
import customtkinter as ctk
from app.views.dialogue_base import DialogueBase
from app.utils import employes_dao
from app.utils.polycliniques_dao import lister_polycliniques
from app.utils.services import SERVICES_CLINIQUES, GRADES
from app.utils.database import get_connection
from app.utils.theme import COULEURS, POLICES, DIMENSIONS

POSTES_PAR_GRADE = {
    "Médecin": [
        "Généraliste", "Médecin des Urgences",
        "Médecin Spécialiste", "Médecin Chef",
    ],
    "Médecin Spécialiste": [
        "Cardiologue", "Pneumologue",
        "Pédiatre", "Gynécologue",
        "Ophtalmologue", "Dermatologue",
        "Neurologue", "Endocrinologue", "ORL",
    ],
    "Ambulancier (OP)": [
        "Conducteur de niveau 1",
        "Conducteur de niveau 2",
        "Ambulancier Principal",
    ],
    "Agent de Sécurité (OP)": [
        "Agent de Sécurité",
        "Chef d'Équipe Sécurité",
    ],
    "Infirmière": [
        "Infirmière de Soins",
        "Infirmière Principale",
        "Infirmière Chef",
        "Infirmière des Urgences",
    ],
    "Infirmier": [
        "Infirmier de Soins",
        "Infirmier Principal",
        "Infirmier Chef",
    ],
}


class DialogueEmploye(DialogueBase):
    def __init__(self, parent, emp_id=None,
                 callback_succes=None):
        self._emp_id   = emp_id
        self._callback = callback_succes
        self._donnees  = (
            employes_dao.obtenir_employe(emp_id)
            if emp_id else None)
        self._depts = employes_dao.lister_departements()
        self._polys = lister_polycliniques()
        self._soldes_rows = []  # lignes dynamiques

        titre = ("Modifier" if emp_id
                 else "＋  Nouvel employé")
        super().__init__(parent, titre=titre,
                         largeur=580, hauteur=760)

    def _construire_corps(self):
        pad  = 20
        cors = self.frame_corps

        def sep(t, c=None):
            f = ctk.CTkFrame(cors,
                             fg_color="transparent")
            f.pack(fill="x", padx=pad,
                   pady=(14, 4))
            ctk.CTkLabel(
                f, text=t,
                font=POLICES["sous_titre"],
                text_color=c or COULEURS["accent_bleu"]
            ).pack(side="left")
            ctk.CTkFrame(
                f, height=1,
                fg_color=c or COULEURS["bordure_active"]
            ).pack(side="left", fill="x",
                   expand=True, padx=(8, 0))

        def champ(label, ph="", req=False):
            f = ctk.CTkFrame(cors,
                             fg_color="transparent")
            f.pack(fill="x", padx=pad,
                   pady=(0, 8))
            ctk.CTkLabel(
                f,
                text=label + (" *" if req else ""),
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w")
            e = ctk.CTkEntry(
                f, placeholder_text=ph,
                fg_color=COULEURS["bg_champ"],
                border_color=COULEURS["bordure"],
                text_color=COULEURS["texte_principal"],
                placeholder_text_color=COULEURS["texte_discret"],
                font=POLICES["corps"],
                height=36,
                corner_radius=DIMENSIONS["rayon_bouton"])
            e.pack(fill="x", pady=(4, 0))
            return e

        def menu(label, vals, req=False, cmd=None):
            f = ctk.CTkFrame(cors,
                             fg_color="transparent")
            f.pack(fill="x", padx=pad,
                   pady=(0, 8))
            ctk.CTkLabel(
                f,
                text=label + (" *" if req else ""),
                font=POLICES["corps_bold"],
                text_color=COULEURS["texte_secondaire"]
            ).pack(anchor="w")
            m = ctk.CTkOptionMenu(
                f, values=vals,
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
                height=36, command=cmd)
            m.pack(fill="x", pady=(4, 0))
            return m

        # ── Section 1 ─────────────────────────────
        sep("① Identification")
        self.e_nom      = champ("Nom", "BENSALEM",
                                req=True)
        self.e_prenom   = champ("Prénom", "Kamel",
                                req=True)
        self.e_matricule = champ(
            "Matricule", "Ex : MR-001")

        # Année entrée
        f_ae = ctk.CTkFrame(cors,
                            fg_color="transparent")
        f_ae.pack(fill="x", padx=pad,
                  pady=(0, 8))
        ctk.CTkLabel(
            f_ae, text="Année d'entrée",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        annees = [str(y) for y in range(
            datetime.date.today().year,
            datetime.date.today().year - 40, -1)]
        self.m_annee_ent = ctk.CTkOptionMenu(
            f_ae, values=annees,
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=36)
        self.m_annee_ent.pack(fill="x",
                              pady=(4, 0))

        # ── Section 2 ─────────────────────────────
        sep("② Affectation")

        noms_polys = (
            ["— Sélectionner —"] +
            [p["nom"] for p in self._polys])
        self.m_poly = menu(
            "Polyclinique", noms_polys, req=True)

        self.m_service = menu(
            "Service clinique",
            SERVICES_CLINIQUES)

        # ── Section 3 ─────────────────────────────
        sep("③ Grade & Poste")
        self.m_grade = menu(
            "Grade / Corps", GRADES, req=True,
            cmd=self._on_grade)

        # Poste dynamique
        f_ps = ctk.CTkFrame(cors,
                            fg_color="transparent")
        f_ps.pack(fill="x", padx=pad,
                  pady=(0, 8))
        ctk.CTkLabel(
            f_ps, text="Poste occupé",
            font=POLICES["corps_bold"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(anchor="w")
        self.frame_poste_w = ctk.CTkFrame(
            f_ps, fg_color="transparent")
        self.frame_poste_w.pack(fill="x",
                                pady=(4, 0))
        self.m_poste = ctk.CTkOptionMenu(
            self.frame_poste_w,
            values=["Poste principal"],
            fg_color=COULEURS["bg_champ"],
            button_color=COULEURS["accent_bleu"],
            button_hover_color=COULEURS["accent_bleu_clair"],
            dropdown_fg_color=COULEURS["bg_carte"],
            dropdown_hover_color=COULEURS["bg_hover"],
            text_color=COULEURS["texte_principal"],
            dropdown_text_color=COULEURS["texte_principal"],
            font=POLICES["corps"],
            corner_radius=DIMENSIONS["rayon_bouton"],
            height=36)
        self.m_poste.pack(fill="x")
        self.e_poste_libre = ctk.CTkEntry(
            self.frame_poste_w,
            placeholder_text="Saisir le poste…",
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            placeholder_text_color=COULEURS["texte_discret"],
            font=POLICES["corps"], height=36,
            corner_radius=DIMENSIONS["rayon_bouton"])
        self.e_poste_libre.pack(fill="x")
        self.e_poste_libre.pack_forget()
        self._poste_mode = "menu"
        self._on_grade(GRADES[0])

        # ── Section 4 : Soldes dynamiques ─────────
        if not self._emp_id:
            sep("④ Soldes initiaux (jours restants)",
                c=COULEURS["accent_vert"])

            ctk.CTkLabel(
                cors,
                text="Entrez uniquement le nombre "
                     "de jours RESTANTS par année.",
                font=POLICES["petit"],
                text_color=COULEURS["texte_secondaire"],
                wraplength=500
            ).pack(anchor="w", padx=pad,
                   pady=(0, 6))

            # Conteneur lignes soldes
            self.frame_soldes_dyn = ctk.CTkFrame(
                cors,
                fg_color=COULEURS["bg_carte"],
                corner_radius=8)
            self.frame_soldes_dyn.pack(
                fill="x", padx=pad, pady=(0, 6))

            # Années par défaut 2022→courante
            annee_cour = datetime.date.today().year
            for a in range(2022, annee_cour + 1):
                self._ajouter_ligne_solde(a)

            # Bouton ajouter une ligne
            ctk.CTkButton(
                cors,
                text="＋  Ajouter une année",
                fg_color=COULEURS["bg_champ"],
                hover_color=COULEURS["bg_hover"],
                text_color=COULEURS["texte_secondaire"],
                font=POLICES["corps"],
                height=30,
                corner_radius=DIMENSIONS["rayon_bouton"],
                command=self._ajouter_ligne_solde
            ).pack(anchor="w", padx=pad,
                   pady=(0, 10))

        # Erreur
        self._lbl_erreur = ctk.CTkLabel(
            cors, text="",
            font=POLICES["corps"],
            text_color=COULEURS["accent_rouge"],
            fg_color="#2D1515", corner_radius=6)
        self._lbl_erreur.pack(fill="x", padx=pad,
                              pady=(4, 4))

        self.btn_valider.configure(
            text="💾  Enregistrer")

        if self._donnees:
            self._preremplir()

    def _ajouter_ligne_solde(self, annee=None):
        """Ajoute une ligne dynamique année + restant."""
        if annee is None:
            annee = datetime.date.today().year

        f = ctk.CTkFrame(
            self.frame_soldes_dyn,
            fg_color="transparent")
        f.pack(fill="x", padx=10, pady=3)

        annee_cour = datetime.date.today().year
        is_old = annee < annee_cour

        ctk.CTkLabel(
            f,
            text=f"{'🔴' if is_old else '✅'} "
                 f"Année {annee} :",
            font=POLICES["corps_bold"],
            text_color=(COULEURS["accent_orange"]
                        if is_old
                        else COULEURS["accent_vert"]),
            width=110, anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            f, text="Jours restants :",
            font=POLICES["petit"],
            text_color=COULEURS["texte_secondaire"]
        ).pack(side="left", padx=(8, 4))

        e_restant = ctk.CTkEntry(
            f, width=70,
            fg_color=COULEURS["bg_champ"],
            border_color=COULEURS["bordure"],
            text_color=COULEURS["texte_principal"],
            font=POLICES["corps"], height=30,
            corner_radius=DIMENSIONS["rayon_bouton"])
        e_restant.insert(0, "30")
        e_restant.pack(side="left")

        # Bouton supprimer la ligne
        def _suppr(frame=f, row=None):
            frame.destroy()
            if row in self._soldes_rows:
                self._soldes_rows.remove(row)

        row_ref = [annee, e_restant]
        self._soldes_rows.append(row_ref)

        ctk.CTkButton(
            f, text="✕",
            fg_color="transparent",
            hover_color=COULEURS["accent_rouge"],
            text_color=COULEURS["texte_discret"],
            width=26, height=26,
            corner_radius=4,
            command=lambda r=row_ref:
                _suppr(f, r)
        ).pack(side="left", padx=(6, 0))

    def _on_grade(self, grade):
        postes = POSTES_PAR_GRADE.get(grade)
        for w in self.frame_poste_w.winfo_children():
            w.pack_forget()
        if postes:
            self.m_poste.configure(values=postes)
            self.m_poste.set(postes[0])
            self.m_poste.pack(fill="x")
            self._poste_mode = "menu"
        else:
            self.e_poste_libre.pack(fill="x")
            self._poste_mode = "libre"

    def _get_poste(self):
        if self._poste_mode == "menu":
            return self.m_poste.get()
        return self.e_poste_libre.get().strip()

    def _preremplir(self):
        d = self._donnees
        self.e_nom.insert(0, d["nom"])
        self.e_prenom.insert(0, d["prenom"])
        if d.get("matricule"):
            self.e_matricule.insert(0, d["matricule"])
        if d.get("annee_entree"):
            self.m_annee_ent.set(
                str(d["annee_entree"]))
        for p in self._polys:
            if p["id"] == d.get("polyclinique_id"):
                self.m_poly.set(p["nom"])
                break
        if d.get("grade") in GRADES:
            self.m_grade.set(d["grade"])
            self._on_grade(d["grade"])

    def _valider(self):
        self._cacher_erreur()

        nom    = self.e_nom.get().strip().upper()
        prenom = self.e_prenom.get().strip()
        grade  = self.m_grade.get()
        poly_s = self.m_poly.get()

        # Obligatoires uniquement
        if not nom:
            self._afficher_erreur("Nom obligatoire.")
            return
        if not prenom:
            self._afficher_erreur(
                "Prénom obligatoire.")
            return
        if not grade or grade == GRADES[-1]:
            pass  # Autre accepté
        if (not poly_s or
                "Sélectionner" in poly_s):
            self._afficher_erreur(
                "Polyclinique obligatoire.")
            return

        mat = self.e_matricule.get().strip().upper()
        if mat and employes_dao.matricule_existe(
                mat, exclure_id=self._emp_id):
            self._afficher_erreur(
                f"Matricule « {mat} » déjà utilisé.")
            return

        poly_id = next(
            (p["id"] for p in self._polys
             if p["nom"] == poly_s), None)

        svc = self.m_service.get() \
            if hasattr(self, "m_service") else ""
        dept_id = self._resoudre_dept(svc)

        try:
            annee_ent = int(
                self.m_annee_ent.get())
        except Exception:
            annee_ent = None

        data = {
            "matricule":       mat or f"AUTO-{nom[:4]}",
            "nom":             nom,
            "prenom":          prenom,
            "grade":           grade,
            "poste":           self._get_poste(),
            "departement_id":  dept_id,
            "polyclinique_id": poly_id,
            "est_manip_radio": (
                1 if "Radio" in grade else 0),
            "annee_entree":    annee_ent,
            "actif":           True,
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
            # Fermeture propre
            self.destroy()

        except Exception as ex:
            self._afficher_erreur(f"Erreur: {ex}")

    def _resoudre_dept(self, service: str) -> int:
        conn = get_connection()
        code = (service[:12]
                .upper()
                .replace(" ", "_")
                .replace("/", "_"))
        row = conn.execute(
            "SELECT id FROM departements "
            "WHERE code=?", (code,)
        ).fetchone()
        if row:
            conn.close()
            return row["id"]
        cur = conn.execute(
            "INSERT OR IGNORE INTO departements "
            "(code, nom) VALUES (?,?)",
            (code, service))
        conn.commit()
        rid = cur.lastrowid or conn.execute(
            "SELECT id FROM departements "
            "WHERE code=?", (code,)
        ).fetchone()["id"]
        conn.close()
        return rid

    def _creer_avec_soldes(self, data) -> int:
        conn = get_connection()
        cur  = conn.execute("""
            INSERT INTO employes
                (matricule, nom, prenom, grade,
                 poste, departement_id,
                 polyclinique_id, est_manip_radio,
                 annee_entree, actif)
            VALUES (?,?,?,?,?,?,?,?,?,1)
        """, (
            data["matricule"], data["nom"],
            data["prenom"], data["grade"],
            data["poste"], data["departement_id"],
            data.get("polyclinique_id"),
            data.get("est_manip_radio", 0),
            data.get("annee_entree"),
        ))
        emp_id = cur.lastrowid

        for row in self._soldes_rows:
            annee, e_restant = row
            try:
                restant = float(
                    e_restant.get().strip() or "0")
                restant = max(0.0, restant)
            except ValueError:
                restant = 0.0

            if restant > 0:
                conn.execute("""
                    INSERT OR IGNORE INTO
                    conges_annuels
                        (employe_id, annee,
                         jours_initiaux,
                         jours_utilises)
                    VALUES (?,?,?,0)
                """, (emp_id, annee, restant))

        # Année courante si aucun solde
        if not self._soldes_rows:
            annee = datetime.date.today().year
            conn.execute("""
                INSERT OR IGNORE INTO
                conges_annuels
                    (employe_id, annee,
                     jours_initiaux,
                     jours_utilises)
                VALUES (?,?,30,0)
            """, (emp_id, annee))

        conn.commit()
        conn.close()
        return emp_id
