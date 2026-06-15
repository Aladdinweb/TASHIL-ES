# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_connection, initialize_database

DEPARTEMENTS = [
    ("ISP",        "Inspection Sanitaire et de la Prévention", "Service ISP"),
    ("MANIP-RADIO","Manipulateurs en Radiologie",              "Service Radiologie"),
    ("CHURG-DENT", "Chirurgie Dentaire",                       "Service Dentaire"),
    ("MED-SPEC",   "Médecines Spécialistes",                   "Spécialités médicales"),
    ("ADMIN",      "Administration Générale",                  "Secrétariat et RH"),
    ("PHARMACO",   "Pharmacie",                                "Pharmacie hospitalière"),
    ("BLOC-OP",    "Bloc Opératoire",                          "Chirurgie et anesthésie"),
    ("URGENCES",   "Service des Urgences",                     "Urgences 24h/24"),
]

EMPLOYES = [
    ("ISP-001","BENALI",   "Karim",   "Médecin",             "Médecin Inspecteur",      "ISP",        0),
    ("ISP-002","RAHMANI",  "Farida",  "Technicien Supérieur","Technicienne Sanitaire",  "ISP",        0),
    ("MR-001", "KACI",     "Mourad",  "Manipulateur Radio",  "Manipulateur Principal",  "MANIP-RADIO",1),
    ("MR-002", "AISSAOUI", "Sonia",   "Manipulateur Radio",  "Manipulatrice",           "MANIP-RADIO",1),
    ("MR-003", "HAMDI",    "Youcef",  "Manipulateur Radio",  "Manipulateur",            "MANIP-RADIO",1),
    ("CD-001", "MEZIANE",  "Amina",   "Chirurgien Dentiste", "Chirurgienne Dentiste",   "CHURG-DENT", 0),
    ("CD-002", "TALEB",    "Riad",    "Aide Soignant",       "Assistant Dentaire",      "CHURG-DENT", 0),
    ("MS-001", "BOUDIAF",  "Leila",   "Médecin Spécialiste", "Cardiologue",             "MED-SPEC",   0),
    ("MS-002", "CHERIF",   "Omar",    "Médecin Spécialiste", "Pneumologue",             "MED-SPEC",   0),
    ("MS-003", "HADJ",     "Nadia",   "Infirmière",          "Infirmière Principale",   "MED-SPEC",   0),
    ("ADM-001","SAIDI",    "Fatiha",  "Administrateur",      "Responsable RH",          "ADMIN",      0),
    ("ADM-002","MELLOUK",  "Tarek",   "Agent Administratif", "Secrétaire",              "ADMIN",      0),
    ("PH-001", "GUESSOUM", "Yasmine", "Pharmacien",          "Pharmacienne Principale", "PHARMACO",   0),
    ("BO-001", "OUALI",    "Samir",   "Infirmier Anesthésiste","IADE",                  "BLOC-OP",    0),
    ("BO-002", "FEKIR",    "Houria",  "Infirmière",          "Infirmière de Bloc",      "BLOC-OP",    0),
    ("URG-001","MANSOURI", "Djamel",  "Médecin",             "Médecin Urgentiste",      "URGENCES",   0),
    ("URG-002","BOUZIDI",  "Samira",  "Infirmière",          "Infirmière des Urgences", "URGENCES",   0),
]

SOLDES = [
    ("ISP-001",2024,30.0,12.0),("ISP-001",2025,30.0,0.0),
    ("ISP-002",2024,30.0,30.0),("ISP-002",2025,30.0,5.0),
    ("MR-001", 2024,30.0,10.0),("MR-001", 2025,30.0,0.0),
    ("MR-002", 2024,30.0,20.0),("MR-002", 2025,30.0,0.0),
    ("MR-003", 2025,30.0,0.0),
    ("CD-001", 2024,30.0,15.0),("CD-001", 2025,30.0,0.0),
    ("MS-001", 2024,30.0,30.0),("MS-001", 2025,30.0,8.0),
    ("MS-002", 2025,30.0,0.0),("MS-003", 2025,30.0,0.0),
    ("ADM-001",2024,30.0,22.0),("ADM-001",2025,30.0,0.0),
    ("ADM-002",2025,30.0,0.0),
    ("PH-001", 2025,30.0,0.0),
    ("BO-001", 2024,30.0,18.0),("BO-001", 2025,30.0,0.0),
    ("BO-002", 2025,30.0,0.0),
    ("URG-001",2024,30.0,30.0),("URG-001",2025,30.0,10.0),
    ("URG-002",2025,30.0,0.0),
]

def seed():
    initialize_database()
    conn = get_connection()
    c = conn.cursor()

    print("\n--- Départements ---")
    for code, nom, desc in DEPARTEMENTS:
        try:
            c.execute("INSERT INTO departements (code,nom,description) VALUES (?,?,?)",(code,nom,desc))
            print(f"  [+] {code}")
        except: print(f"  [=] {code} existant")

    print("\n--- Employés ---")
    for mat,nom,prenom,grade,poste,dept,radio in EMPLOYES:
        try:
            row = c.execute("SELECT id FROM departements WHERE code=?",(dept,)).fetchone()
            if not row: print(f"  [!] Dept introuvable: {dept}"); continue
            c.execute("INSERT INTO employes (matricule,nom,prenom,grade,poste,departement_id,est_manip_radio) VALUES (?,?,?,?,?,?,?)",
                      (mat,nom,prenom,grade,poste,row["id"],radio))
            print(f"  [+] {mat} — {nom} {prenom}")
        except: print(f"  [=] {mat} existant")

    print("\n--- Soldes de congé ---")
    for mat,annee,init,util in SOLDES:
        try:
            row = c.execute("SELECT id FROM employes WHERE matricule=?",(mat,)).fetchone()
            if not row: print(f"  [!] Employé introuvable: {mat}"); continue
            c.execute("INSERT INTO conges_annuels (employe_id,annee,jours_initiaux,jours_utilises) VALUES (?,?,?,?)",
                      (row["id"],annee,init,util))
            print(f"  [+] {mat}/{annee} → {init-util:.0f}j restants")
        except: print(f"  [=] {mat}/{annee} existant")

    conn.commit()
    conn.close()
    print("\n[OK] Données insérées avec succès.\n")

if __name__ == "__main__":
    seed()
