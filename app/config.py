# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Configuration centralisée — TASHIL
Smart Health Management System
"""

APP_NAME        = "TASHIL"
APP_TAGLINE     = "Smart Health Management System"
APP_FULL_NAME   = f"{APP_NAME}: {APP_TAGLINE}"
APP_AUTHOR      = "ILINE TECH — FERAK ALADDIN"
APP_YEAR        = "2026"
APP_GITHUB      = "Aladdinweb/epsp-conge-manager"

# Contexte institutionnel
INSTITUTION     = "EPSP"
MINISTERE       = "وزارة الصحة"
REPUBLIQUE      = "الجمهورية الجزائرية الديمقراطية الشعبية"

# Fenêtre
WINDOW_TITLE_TEMPLATE = (
    "{app} — {poly} — v{version}")

# Services cliniques officiels (18)
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

# Hiérarchie administrative
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

# Postes suggérés par grade
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
}
