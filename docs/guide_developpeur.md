# Guide pour les devs

Si tu dois reprendre mon code ou recompiler l'application pour la mettre à jour, voici tout ce qu'il faut savoir.

## Pour installer l'environnement de dev

Le projet tourne sous Python (j'ai utilisé la version 3.10+).

1. Récupère le dossier du projet.
2. Ouvre un terminal dans le dossier et crée un environnement virtuel pour pas polluer ton PC :
   ```bash
   python -m venv venv
   ```
3. Active-le (sous Windows c'est ça) :
   ```bash
   .\venv\Scripts\activate
   ```
4. Installe toutes les librairies que j'ai utilisées :
   ```bash
   pip install -r requirements.txt
   ```

## Comment le code est organisé

J'ai essayé de faire un truc à peu près propre dans le dossier `src/` :

- `app_questionnaires.py` : C'est le fichier principal. Dedans, il y a toute l'interface graphique (faite avec `customtkinter`, c'est plus joli que le tkinter de base). C'est là aussi que je gère les deux onglets et l'export Excel.
- `analyse_questionnaires.py` : C'est un peu le moteur de calcul. Il s'occupe de lire le CSV, de faire les stats, et de pondre le PDF avec `matplotlib` (pour les graphiques) et `fpdf2` (pour le document).

## Comment tester et compiler en .exe

Pour lancer le script normal :

```bash
python src/app_questionnaires.py
```

Et **LE** truc important : si tu fais des modifs et que tu veux donner l'application à quelqu'un qui n'a pas Python d'installé, il faut refaire le `.exe`.
Assure-toi que le `venv` est bien activé, et tape cette commande magique :

```bash
pyinstaller --noconsole --onefile --name "App_Questionnaires_CHCahors" src/app_questionnaires.py
```

- `--onefile` c'est pour que ça fasse un seul gros exécutable (plus simple à partager).
- `--noconsole` ça évite d'avoir la fenêtre noire CMD qui s'ouvre derrière l'appli.

L'exécutable tout neuf sera dans le dossier `dist/`.

## Petit détail sur la sauvegarde

Quand on coche des cases dans l'appli et qu'on fait "Sauvegarder", ça crée un fichier `config_obligatoires.json` dans un dossier `application/` juste à côté de l'exécutable. C'est normal, c'est pour garder la config en mémoire d'une session à l'autre.

## Logique et points importants du code

L'application est découpée en deux scripts principaux pour séparer l'interface graphique du moteur de traitement.

### 1. `app_questionnaires.py` (Interface Graphique)
Ce fichier gère toute la logique visuelle avec la librairie `customtkinter`.

- **Onglet "Configuration Obligatoires"** : Permet de charger le fichier CSV de données (dont le séparateur attendu est `|`). L'application détecte automatiquement tous les services ("QUESTIONNAIRE") et leurs questions associées. L'utilisateur coche ensuite les questions considérées comme obligatoires.
- **Sauvegarde** : Les choix sont enregistrés dans le fichier `application/config_obligatoires.json` grâce à la méthode `_save_config()`.
- **Onglet "Contrôle Qualité"** : Permet de tirer au sort un échantillon (ex: 10 réponses) de réponses non vides pour un service et des questions spécifiques, puis d'exporter ces lignes dans un fichier Excel formaté via la librairie `openpyxl`.
- **Génération PDF** : Le bouton "Générer le PDF" appelle les fonctions d'analyse du second script pour produire le rapport.

### 2. `analyse_questionnaires.py` (Moteur d'Analyse et PDF)
Ce script est le cœur métier de l'application. Il ne dépend d'aucune interface graphique et pourrait même être utilisé en ligne de commande.

- **Lecture des données (`lire_csv`)** : Lit le fichier CSV bloc par bloc et ignore les en-têtes répétés (qui arrivent souvent avec certains exports hospitaliers).
- **Calcul des statistiques (`analyser_completude`)** : Croise les données CSV avec la configuration `config_obligatoires.json` pour calculer le taux de complétion (nombre de réponses vides vs totales) pour chaque question obligatoire.
- **Graphiques (`matplotlib`)** : Le script utilise `matplotlib` avec le backend "Agg" (non-interactif) pour générer des images temporaires (camembert global, graphiques en barres par service).
- **Création du PDF (`RapportPDF`)** : Utilise la librairie `fpdf2`. Une classe personnalisée `RapportPDF` hérite de `FPDF` pour définir des en-têtes, pieds de page, et inclure des polices compatibles UTF-8 (`DejaVuSans` récupérée depuis `matplotlib`) afin d'éviter les bugs d'affichage des accents. Les images temporaires y sont insérées puis supprimées à la fin du processus.
