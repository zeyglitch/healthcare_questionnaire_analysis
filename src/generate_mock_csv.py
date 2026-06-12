"""
Génération d'un fichier CSV mock pour la mission 2.

Ce script crée un fichier CSV simulant l'export de formulaires/questionnaires
remplis dans les différents services d'un hôpital.

Format de sortie :
  - Séparateur : | (pipe)
  - Valeurs entourées de guillemets doubles
  - Encodage : UTF-8 avec BOM (compatible Excel)

Colonnes :
  1. IPP              — Identifiant Permanent du Patient (fixe par patient)
  2. NDA              — Numéro de Dossier Administratif (un par séjour)
  3. ID_Service       — Identifiant du service hospitalier
  4. Nom_Service      — Nom du service
  5. ID_Patient       — Identifiant anonymisé du patient (ex: PAT-XXXXX)
  6. Date_Saisie      — Date de saisie du formulaire (JJ/MM/AAAA)
  7. Medecin          — Nom du médecin responsable (fictif)
  8. UF               — Unité fonctionnelle
  9. Questionnaire    — Nom du questionnaire/formulaire
  10. Réponse         — Réponse saisie

Usage :
  python generate_mock_csv.py
  python generate_mock_csv.py --output mon_fichier.csv --lignes 500
"""

import csv
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path


# ──────────────────────────────────────────────
#  Données de référence pour la génération
# ──────────────────────────────────────────────

SERVICES = [
    ("SRV-001", "Cardiologie",             "UF-110"),
    ("SRV-002", "Pneumologie",             "UF-120"),
    ("SRV-003", "Neurologie",              "UF-130"),
    ("SRV-004", "Chirurgie Orthopédique",  "UF-210"),
    ("SRV-005", "Médecine Interne",        "UF-310"),
    ("SRV-006", "Gériatrie",              "UF-320"),
    ("SRV-007", "Pédiatrie",              "UF-410"),
    ("SRV-008", "Urgences",                "UF-500"),
    ("SRV-009", "Réanimation",            "UF-510"),
    ("SRV-010", "SSR",                     "UF-600"),
    ("SRV-011", "Oncologie",               "UF-710"),
    ("SRV-012", "Gastro-entérologie",     "UF-720"),
    ("SRV-013", "Maternité",              "UF-810"),
]

PRENOMS = [
    "Jean", "Marie", "Pierre", "Sophie", "Laurent", "Isabelle", "François",
    "Catherine", "Philippe", "Nathalie", "Michel", "Sandrine", "Alain",
    "Véronique", "Christophe", "Valérie", "Thierry", "Sylvie", "Éric",
    "Anne", "Patrick", "Martine", "Olivier", "Brigitte", "Nicolas",
    "Céline", "Stéphane", "Hélène", "Bruno", "Corinne",
]

NOMS = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier",
    "Morel", "Girard", "André", "Mercier", "Dupont", "Lambert", "Bonnet",
    "François", "Martinez", "Legrand",
]

# ──────────────────────────────────────────────
#  Questionnaires et réponses possibles
# ──────────────────────────────────────────────

QUESTIONNAIRES = {
    # ── Évaluation de la douleur ──
    "EVA - Échelle Visuelle Analogique": [
        "0/10 - Aucune douleur",
        "1/10 - Douleur très faible",
        "2/10 - Douleur faible",
        "3/10 - Douleur légère",
        "4/10 - Douleur modérée",
        "5/10 - Douleur moyenne",
        "6/10 - Douleur forte",
        "7/10 - Douleur très forte",
        "8/10 - Douleur intense",
        "9/10 - Douleur très intense",
        "10/10 - Douleur insupportable",
    ],
    "EN - Échelle Numérique Douleur": [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    ],
    "Algoplus (douleur personne âgée)": [
        "0/5 - Pas de douleur",
        "1/5 - Douleur faible",
        "2/5 - Douleur modérée",
        "3/5 - Douleur importante",
        "4/5 - Douleur sévère",
        "5/5 - Douleur très sévère",
    ],

    # ── Autonomie / dépendance ──
    "Indice de Katz (ADL)": [
        "6/6 - Autonomie complète",
        "5/6 - Dépendance très légère",
        "4/6 - Dépendance légère",
        "3/6 - Dépendance modérée",
        "2/6 - Dépendance sévère",
        "1/6 - Dépendance très sévère",
        "0/6 - Dépendance totale",
    ],
    "GIR - Grille AGGIR": [
        "GIR 1 - Dépendance totale",
        "GIR 2 - Dépendance sévère",
        "GIR 3 - Autonomie partielle conservée",
        "GIR 4 - Aide ponctuelle nécessaire",
        "GIR 5 - Aide ponctuelle légère",
        "GIR 6 - Autonomie complète",
    ],
    "Barthel (autonomie fonctionnelle)": [
        "100/100 - Indépendant",
        "80/100 - Légèrement dépendant",
        "60/100 - Modérément dépendant",
        "40/100 - Sévèrement dépendant",
        "20/100 - Très sévèrement dépendant",
        "0/100 - Totalement dépendant",
    ],
    "MIF - Mesure d'Indépendance Fonctionnelle": [
        "126/126 - Indépendance complète",
        "108/126 - Indépendance modifiée",
        "90/126 - Supervision nécessaire",
        "72/126 - Aide minimale",
        "54/126 - Aide modérée",
        "36/126 - Aide maximale",
        "18/126 - Aide totale",
    ],

    # ── Nutrition ──
    "MNA - Mini Nutritional Assessment": [
        "Score >= 24 : État nutritionnel normal",
        "Score 17-23.5 : Risque de malnutrition",
        "Score < 17 : Mauvais état nutritionnel",
    ],
    "NRS 2002 - Dépistage nutritionnel": [
        "Score 0 : Pas de risque",
        "Score 1 : Risque faible",
        "Score 2 : Risque modéré",
        "Score >= 3 : Risque élevé - Plan nutritionnel requis",
    ],
    "SEFI - Score d'évaluation alimentaire": [
        "Apports normaux (> 2/3 des repas)",
        "Apports diminués (1/2 à 2/3 des repas)",
        "Apports très diminués (< 1/2 des repas)",
        "Apports quasi nuls",
    ],

    # ── État cognitif / confusion ──
    "MMSE - Mini Mental State Examination": [
        "30/30 - Normal",
        "27/30 - Normal",
        "24/30 - Léger déficit",
        "20/30 - Déficit modéré",
        "15/30 - Déficit modéré à sévère",
        "10/30 - Déficit sévère",
        "5/30 - Déficit très sévère",
    ],
    "CAM - Confusion Assessment Method": [
        "Positif - Confusion aiguë présente",
        "Négatif - Pas de confusion aiguë",
    ],
    "Test de l'horloge": [
        "Normal (score 4-5)",
        "Anomalie légère (score 3)",
        "Anomalie modérée (score 2)",
        "Anomalie sévère (score 0-1)",
    ],

    # ── Risque d'escarres ──
    "Échelle de Braden": [
        "Score >= 19 : Pas de risque",
        "Score 15-18 : Risque faible",
        "Score 13-14 : Risque modéré",
        "Score 10-12 : Risque élevé",
        "Score <= 9 : Risque très élevé",
    ],
    "Échelle de Norton": [
        "Score >= 14 : Pas de risque",
        "Score 12-13 : Risque modéré",
        "Score <= 11 : Risque élevé",
    ],

    # ── Risque de chute ──
    "Test de Tinetti (équilibre et marche)": [
        "Score >= 24 : Pas de risque de chute",
        "Score 20-23 : Risque faible",
        "Score < 20 : Risque élevé de chute",
    ],
    "Get Up and Go Test": [
        "< 10 sec - Normal",
        "10-19 sec - Bonne mobilité",
        "20-29 sec - Mobilité réduite",
        ">= 30 sec - Risque de chute élevé",
    ],

    # ── Évaluation psychologique ──
    "GDS - Échelle de dépression gériatrique": [
        "Score 0-5 : Normal",
        "Score 6-10 : Dépression légère",
        "Score 11-15 : Dépression sévère",
    ],
    "HAD - Hospital Anxiety and Depression": [
        "Anxiété 0-7 / Dépression 0-7 : Normal",
        "Anxiété 8-10 / Dépression 8-10 : Douteuse",
        "Anxiété >= 11 / Dépression >= 11 : Certaine",
    ],
    "Mini GDS": [
        "Score 0 : Pas de dépression",
        "Score >= 1 : Suspicion de dépression",
    ],

    # ── Satisfaction patient ──
    "Questionnaire de satisfaction - Séjour": [
        "Très satisfait",
        "Satisfait",
        "Moyennement satisfait",
        "Peu satisfait",
        "Pas du tout satisfait",
    ],
    "Questionnaire de satisfaction - Repas": [
        "Très satisfait",
        "Satisfait",
        "Moyennement satisfait",
        "Insatisfait",
    ],
    "Questionnaire de satisfaction - Prise en charge": [
        "Excellente",
        "Bonne",
        "Correcte",
        "Insuffisante",
        "Mauvaise",
    ],

    # ── Évaluation plaies / pansements ──
    "Évaluation plaie - Stade escarre": [
        "Stade 1 - Érythème persistant",
        "Stade 2 - Phlyctène / abrasion",
        "Stade 3 - Perte de substance",
        "Stade 4 - Atteinte os/muscle",
        "Inclassable",
    ],
    "Évaluation plaie - Évolution": [
        "Amélioration",
        "Stable",
        "Dégradation",
    ],

    # ── Consentement / formulaires administratifs ──
    "Consentement éclairé": [
        "Oui - Consentement signé",
        "Non - Refus du patient",
        "En attente - Délai de réflexion",
    ],
    "Personne de confiance désignée": [
        "Oui",
        "Non",
        "Non applicable",
    ],
    "Directives anticipées": [
        "Oui - Rédigées",
        "Non - Non rédigées",
        "En cours de rédaction",
        "Non applicable",
    ],

    # ── Évaluation respiratoire ──
    "Échelle de Borg (dyspnée)": [
        "0 - Aucune dyspnée",
        "1 - Très très légère",
        "2 - Très légère",
        "3 - Légère",
        "4 - Modérée",
        "5 - Assez sévère",
        "6 - Sévère",
        "7 - Très sévère",
        "8 - Très très sévère",
        "9 - Quasi maximale",
        "10 - Maximale",
    ],
    "Score de Glasgow": [
        "15/15 - Conscience normale",
        "14/15",
        "13/15",
        "12/15 - Confusion",
        "9/15 - Coma léger",
        "6/15 - Coma profond",
        "3/15 - Coma dépassé",
    ],
}

# Pondération : certains questionnaires sont plus fréquents que d'autres
QUESTIONNAIRE_POIDS = {
    "EVA - Échelle Visuelle Analogique": 15,
    "EN - Échelle Numérique Douleur": 12,
    "Indice de Katz (ADL)": 8,
    "GIR - Grille AGGIR": 6,
    "Barthel (autonomie fonctionnelle)": 5,
    "Questionnaire de satisfaction - Séjour": 10,
    "Questionnaire de satisfaction - Repas": 5,
    "Questionnaire de satisfaction - Prise en charge": 8,
    "Consentement éclairé": 10,
    "Personne de confiance désignée": 6,
    "Score de Glasgow": 4,
}


def generer_id_patient() -> str:
    """Génère un identifiant patient anonymisé au format PAT-XXXXX."""
    return f"PAT-{random.randint(10000, 99999)}"


def generer_ipp() -> str:
    """Génère un IPP (Identifiant Permanent du Patient) au format 8 chiffres."""
    return f"{random.randint(10000000, 99999999)}"


def generer_nda() -> str:
    """Génère un NDA (Numéro de Dossier Administratif) au format 10 chiffres."""
    return f"{random.randint(1000000000, 9999999999)}"


def generer_medecin() -> str:
    """Génère un nom de médecin fictif au format Dr Prénom NOM."""
    prenom = random.choice(PRENOMS)
    nom = random.choice(NOMS)
    return f"Dr {prenom} {nom.upper()}"


def generer_date(debut: datetime, fin: datetime) -> str:
    """Génère une date aléatoire entre debut et fin au format JJ/MM/AAAA."""
    delta = fin - debut
    jours_aleatoires = random.randint(0, delta.days)
    date = debut + timedelta(days=jours_aleatoires)
    return date.strftime("%d/%m/%Y")


def choisir_reponse(question: str) -> str:
    """
    Choisit une réponse aléatoire parmi les réponses possibles de cette question.
    """
    return random.choice(QUESTIONNAIRES[question])

# Génération des questions fixes pour chaque service
QUESTIONS_PAR_SERVICE = {}
for id_srv, nom_srv, uf in SERVICES:
    rng = random.Random(nom_srv)  # Graine fixe par service pour un résultat constant
    noms_questionnaires = list(QUESTIONNAIRES.keys())
    # Chaque service a entre 6 et 12 questions
    nb_q = rng.randint(6, 12)
    QUESTIONS_PAR_SERVICE[nom_srv] = rng.sample(noms_questionnaires, nb_q)


def generer_pool_medecins(n: int = 40) -> list[str]:
    """Génère un pool fixe de médecins pour la cohérence des données."""
    medecins = set()
    while len(medecins) < n:
        medecins.add(generer_medecin())
    return list(medecins)


def generer_pool_patients(n: int = 300) -> list[dict]:
    """
    Génère un pool fixe de patients pour la cohérence des données.
    """
    patients = []
    for _ in range(n):
        patients.append({
            "nip": generer_ipp(),
            "ndas": [generer_nda() for _ in range(random.randint(1, 4))],
            "nom": random.choice(NOMS).upper(),
            "prenom": random.choice(PRENOMS).upper(),
            "date_nais": generer_date(datetime(1940, 1, 1), datetime(2005, 1, 1)),
        })
    return patients


def generer_csv(
    fichier_sortie: str = "export_questionnaires_mock.csv",
    nb_lignes: int = 1000,
    date_debut: datetime | None = None,
    date_fin: datetime | None = None,
    seed: int | None = None,
) -> None:
    """
    Génère le fichier CSV mock.

    Args:
        fichier_sortie: Chemin du fichier CSV de sortie.
        nb_lignes: Nombre de lignes de données à générer.
        date_debut: Date de début de la plage de saisie.
        date_fin: Date de fin de la plage de saisie.
        seed: Graine pour la reproductibilité (optionnel).
    """
    if seed is not None:
        random.seed(seed)

    if date_debut is None:
        date_debut = datetime(2024, 1, 1)
    if date_fin is None:
        date_fin = datetime(2026, 6, 10)

    # Pools pour la cohérence
    pool_medecins = generer_pool_medecins(40)
    pool_patients = generer_pool_patients(300)

    # Associer des médecins à des services (un médecin peut être dans 1-2 services)
    medecin_services: dict[str, list[tuple[str, str, str]]] = {}
    for medecin in pool_medecins:
        nb_services = random.choices([1, 2], weights=[70, 30], k=1)[0]
        services_du_medecin = random.sample(SERVICES, nb_services)
        medecin_services[medecin] = services_du_medecin

    # Entête
    entete = [
        "NIP",
        "NDA",
        "NOM",
        "PRENOM",
        "DATE NAIS",
        "DATEVALEUR",
        "QUESTIONNAIRE",
        "Responsable",
        "Métier",
        "QUESTION",
        "REPONSE",
    ]

    chemin = Path(fichier_sortie)

    # On ne va pas utiliser writer.writerow pour l'entête global car on l'écrit par bloc
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        # On va écrire manuellement pour avoir le contrôle sur les lignes vides
        
        for i in range(nb_lignes):
            # Ligne vide avant chaque bloc (même le premier, comme dans l'exemple)
            if i > 0 or True:
                f.write("\n")
            
            # En-tête
            f.write("|".join(f'"{col}"' for col in entete) + "\n")
            
            # Un patient, un médecin, une date pour tout le bloc
            medecin = random.choice(pool_medecins)
            id_service, nom_service, uf = random.choice(medecin_services[medecin])
            patient = random.choice(pool_patients)
            nda = random.choice(patient["ndas"])
            date = generer_date(date_debut, date_fin)
            date_valeur = f"{date} {random.randint(8, 20):02d}:{random.randint(0, 59):02d}:00"
            questionnaire_nom = f"DOSSIER {nom_service.upper()}"
            
            # Le questionnaire a une liste fixe de questions pour ce service
            questions_du_service = QUESTIONS_PAR_SERVICE[nom_service]
            
            questions_choisies = []
            for q in questions_du_service:
                r = choisir_reponse(q)
                questions_choisies.append((q, r))
            
            for questionnaire_q, reponse in questions_choisies:
                if random.random() < 0.1:
                    reponse = ""  # vide

                ligne = [
                    patient["nip"],
                    nda,
                    patient["nom"],
                    patient["prenom"],
                    patient["date_nais"],
                    date_valeur,
                    questionnaire_nom,
                    medecin,
                    uf,
                    questionnaire_q,
                    reponse,
                ]
                
                # Formater la ligne avec les guillemets et séparateurs
                ligne_formatee = "|".join(f'"{str(val)}"' if val else '""' for val in ligne)
                f.write(ligne_formatee + "\n")

    print(f"[OK] Fichier genere : {chemin.resolve()}")
    print(f"   > {nb_lignes} questionnaires generes (sous forme de blocs)")
    print(f"   > Separateur : | (pipe)")
    print(f"   > Encodage : UTF-8 avec BOM")
    print(f"   > Periode : {date_debut.strftime('%d/%m/%Y')} -> {date_fin.strftime('%d/%m/%Y')}")


# ──────────────────────────────────────────────
#  Point d'entrée CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Génère un fichier CSV mock simulant l'export de questionnaires hospitaliers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python generate_mock_csv.py
  python generate_mock_csv.py --lignes 500 --output test_petit.csv
  python generate_mock_csv.py --lignes 5000 --seed 42 --debut 2025-01-01 --fin 2025-12-31
        """,
    )
    parser.add_argument(
        "--output", "-o",
        default="export_questionnaires_mock.csv",
        help="Nom du fichier CSV de sortie (défaut: export_questionnaires_mock.csv)",
    )
    parser.add_argument(
        "--lignes", "-n",
        type=int,
        default=1000,
        help="Nombre de lignes à générer (défaut: 1000)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Graine aléatoire pour reproductibilité (optionnel)",
    )
    parser.add_argument(
        "--debut",
        type=str,
        default="2024-01-01",
        help="Date de début au format AAAA-MM-JJ (défaut: 2024-01-01)",
    )
    parser.add_argument(
        "--fin",
        type=str,
        default="2026-06-10",
        help="Date de fin au format AAAA-MM-JJ (défaut: 2026-06-10)",
    )

    args = parser.parse_args()

    date_debut = datetime.strptime(args.debut, "%Y-%m-%d")
    date_fin = datetime.strptime(args.fin, "%Y-%m-%d")

    generer_csv(
        fichier_sortie=args.output,
        nb_lignes=args.lignes,
        date_debut=date_debut,
        date_fin=date_fin,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
