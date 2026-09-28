# Analyse de complétude et contrôle qualité des questionnaires hospitaliers

Application Python de traitement automatisé des exports de questionnaires hospitaliers, développée pour un Département d'Information Médicale (DIM). Génère des rapports PDF de complétude par service et permet le tirage aléatoire d'échantillons pour contrôle qualité.

## Contexte

Développé pendant un stage de 3ème année d'école d'ingénieur (ISIS Castres, partenaire INSA) au Département d'Information Médicale du Centre Hospitalier de Cahors, entre avril et juin 2026. Le concept général de l'applicatif a été défini par le DIM du Centre Hospitalier de Cahors ; le code présenté ici en est la réalisation technique, publiée avec leur accord.

Les questionnaires hospitaliers (recueil de données patients, indicateurs qualité) génèrent des exports CSV volumineux qui nécessitaient jusqu'alors :
- une vérification manuelle du taux de remplissage question par question dans Excel ;
- des tirages aléatoires manuels pour audit qualité.

## Résultats

- Traitement de **plus de 150 000 lignes par mois**.
- Génération automatique de rapports PDF illustrés (taux de complétude, graphiques par service).
- Extraction ciblée et statistiques par service produites en quelques minutes.
- **Validé et déployé en production**, gain estimé de ~1,5 jour de travail par mois.

## Fonctionnalités

- **Analyse de complétude** : chargement d'un export CSV, sélection des questions considérées comme obligatoires pour chaque service, génération d'un rapport PDF détaillant les taux de remplissage.
- **Contrôle qualité par échantillonnage** : tirage aléatoire d'un nombre paramétrable de réponses (10 par défaut) parmi celles qui sont remplies, export Excel pour vérification humaine.
- **Interface graphique moderne** (CustomTkinter) avec configuration persistante (les cases cochées sont sauvegardées en JSON entre deux exécutions).
- **Distribution en exécutable Windows** autonome via PyInstaller.

## Stack technique

- Python 3.9+
- Pandas
- CustomTkinter (interface graphique moderne)
- fpdf2 (génération PDF avec graphiques)
- Matplotlib (visualisations intégrées au PDF)
- openpyxl (exports Excel)
- PyInstaller (distribution `.exe`)

## Confidentialité et publication

- **Publication autorisée** par le maître de stage.
- Code **entièrement générique**, sans référence à un établissement ou à une nomenclature interne.
- Le dossier `donnees/` (jeux d'essais et exports générés) est **exclu du versionnement** via `.gitignore` pour garantir qu'aucune donnée réelle ne puisse être publiée par mégarde.

## Structure

```
├── src/                     # Code source (interface + logique de génération)
├── application/             # Configuration persistante (JSON)
├── docs/
│   ├── guide_utilisateur.md
│   └── guide_developpeur.md
├── requirements.txt
└── .gitignore
```

## Installation

```bash
python -m venv venv
venv\Scripts\Activate.ps1     # Windows
# ou : source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Documentation

- **[Guide utilisateur](guide_utilisateur.md)** — utilisation quotidienne de l'application.
- **[Guide développeur](guide_developpeur.md)** — architecture du code, extension, recompilation du `.exe`.

## Licence

MIT — voir [LICENSE](LICENSE).
