# Guide pour les devs (ou pour le stagiaire suivant !)

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
