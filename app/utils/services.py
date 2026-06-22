# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""Services cliniques officiels EPSP ES-SENIA"""

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


def rang_grade(grade: str) -> int:
    try:
        return HIERARCHIE_GRADES.index(grade)
    except ValueError:
        return len(HIERARCHIE_GRADES)

# Grades officiels EPSP
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
