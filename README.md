# Projet - Analyse et Qualité des Questionnaires (Mission 2)

Salut ! 👋 Bienvenue sur le repo de mon projet de stage au CH Cahors. 

L'objectif de cette application est de faciliter le traitement des exports de questionnaires hospitaliers. Au lieu de tout vérifier à la main dans Excel, l'application permet de faire une analyse automatique de ce qui a été rempli, et d'en sortir un PDF avec des petits graphiques sympas. Il y a aussi un onglet pour faire des tirages au sort de réponses pour faire du contrôle qualité (très pratique pour vérifier que les données sont cohérentes).

## Ce que fait l'application :
- **Analyse de complétude** : On choisit un export CSV, on coche les questions qui sont censées être obligatoires pour chaque service, et ça nous sort un rapport PDF (avec le pourcentage de remplissage).
- **Contrôle Qualité** : On peut tirer au hasard un certain nombre de réponses (10 par défaut) parmi celles qui sont remplies, et ça exporte tout proprement dans un fichier Excel pour vérification.

## Dossiers du projet
- `src/` : C'est là qu'il y a tout le code source (l'interface en CustomTkinter et la logique de génération).
- `application/` : Le dossier où l'app sauvegarde sa configuration (le json avec les cases cochées).
- `donnees/` : C'est là que je mets mes jeux d'essais et que les exports se génèrent par défaut. (Ce dossier n'est pas versionné pour des raisons de confidentialité).

## Documentation
Si tu dois reprendre le projet ou juste utiliser l'application :
- [Guide Utilisateur](guide_utilisateur.md) : Pour comprendre comment utiliser l'interface.
- [Guide Développeur](guide_developpeur.md) : Si tu veux bidouiller le code ou recompiler un `.exe`.
