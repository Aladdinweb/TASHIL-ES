# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Configuration centralisée — TASHIL
Smart Health Management System
"""

# ── Identité de marque ────────────────────────
APP_NAME        = "TASHIL"
APP_TAGLINE     = "Smart Health Management System"
APP_FULL_NAME   = f"{APP_NAME}: {APP_TAGLINE}"
APP_AUTHOR      = "ILINE TECH — FERAK ALADDIN"
APP_YEAR        = "2026"
APP_GITHUB_REPO = "Aladdinweb/epsp-conge-manager"
APP_GITHUB_API  = (
    "https://api.github.com/repos/"
    "Aladdinweb/epsp-conge-manager"
    "/releases/latest"
)

# ── Identité institutionnelle ─────────────────
INSTITUTION  = "EPSP"
MINISTERE_AR = "وزارة الصحة"
REPUBLIQUE_AR = (
    "الجمهورية الجزائرية الديمقراطية الشعبية")
MINISTERE_FR = "Ministère de la Santé"

# ── Template titre fenêtre ────────────────────
WINDOW_TITLE_TEMPLATE = (
    "{app} — {poly} — v{version}")

# ── Smart Hub réseau ──────────────────────────
SMART_HUB_HOST    = "0.0.0.0"   # Écoute toutes interfaces
SMART_HUB_PORT    = 7890         # Port dédié TASHIL
SMART_HUB_SECRET  = "TASHIL2026" # Clé d'appairage
SMART_HUB_TIMEOUT = 30           # Secondes timeout

# ── Services cliniques officiels (20) ─────────
SERVICES_CLINIQUES = [
    "Urgences",
    "Consultation",
    "Dentaire",
    "PMI",
    "Pédiatre",
    "Psychologue",
    "Vaccin",
    "Sage Femme",
    "Salle de Soin",
    "ECG",
    "Pharmacie",
    "Médecine Interne / Endocrinologue",
    "Service Ophtalmologie",
    "Secrétariat",
    "Dentaire Urgences",
    "Dermatologue",
    "Pneumologue",
    "ORL",
    "Administration",
    "Autre",
]

# ── Hiérarchie administrative ─────────────────
HIERARCHIE_GRADES = [
    "Médecin Coordinateur",
    "Médecin Chef",
    "Médecin",
    "Médecin Spécialiste",
    "Chirurgien Dentiste",
    "Pharmacien",
    "Biologiste",
    "Psychologue",
    "Manipulateur Radio",
    "Infirmier Anesthésiste",
    "Sage-Femme",
    "Infirmière",
    "Infirmier",
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

# Alias
GRADES = HIERARCHIE_GRADES

# ── Postes par grade ──────────────────────────
POSTES_PAR_GRADE = {
    "Médecin": [
        "Généraliste",
        "Médecin des Urgences",
        "Médecin Spécialiste",
        "Médecin Chef de Service",
        "Médecin Coordinateur",
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
        "Infirmier des Urgences",
    ],
    "Administrateur (ADM)": [
        "Responsable RH",
        "Responsable Administratif",
        "Secrétaire de Direction",
    ],
    "Sage-Femme": [
        "Sage-Femme",
        "Sage-Femme Principale",
        "Sage-Femme Chef",
    ],
}

# ── Catégories congés (Bordereau) ─────────────
CATEGORIES_BORDEREAU = [
    ("CONGE_ANNUEL",
     "CONGE ANNUEL"),
    ("CERTIFICAT_MEDICAL_ARRET",
     "CERTIFICAT MEDICAL D'ARRET DE TRAVAIL"),
    ("CERTIFICAT_MEDICAL_REPRISE",
     "CERTIFICAT MEDICAL DE REPRISE"),
    ("DEMANDE_3_JOURS_NAISSANCE",
     "DEMANDE DE 3 JOURS DE NAISSANCE"),
    ("DEMANDE_ANNULATION_CONGE",
     "DEMANDE D'ANNULATION DE CONGE"),
]

# ── Types de congé Tableau de Service ─────────
TYPES_SERVICE = [
    "Matin", "Soir", "Nuit",
    "Garde", "Repos", "Congé", "Absent",
]
