# Petit mode d'emploi de l'appli

Voici comment utiliser l'application sans trop se prendre la tête. L'interface est découpée en deux gros onglets selon ce qu'on veut faire.

## 1. Lancement et chargement des données
Déjà, pour lancer le truc, il suffit de double-cliquer sur le fichier `App_Questionnaires_CHCahors.exe`.
La première chose à faire une fois l'appli ouverte, c'est de charger les données :
- Cliquez sur le gros bouton bleu **"Charger le CSV"** à gauche.
- Allez chercher l'export de vos questionnaires (fichier .csv).
- L'appli va mouliner un peu et vous dire combien de services elle a trouvé.

## 2. Faire une analyse globale (L'onglet "Configuration Obligatoires")
L'idée ici, c'est de voir le taux de remplissage des questions importantes.
1. Restez sur le premier onglet. Vous verrez la liste des questionnaires/services.
2. Dépliez ou regardez les questions, et **cochez celles qui sont obligatoires**.
3. *Astuce :* N'oubliez pas de cliquer sur **"Sauvegarder"** à gauche ! Comme ça, au prochain lancement, vous n'aurez pas à tout recocher, ça s'en souvient.
4. Une fois que c'est bon, cliquez sur **"Générer le PDF"** (le bouton rouge en bas à gauche). Il vous demandera où le sauvegarder, et il l'ouvrira tout seul à la fin.

## 3. Faire un tirage au sort (L'onglet "Contrôle Qualité")
Si on a besoin de vérifier que les réponses saisies ont du sens, on peut demander à l'appli d'en piocher quelques-unes au hasard.
1. Cliquez sur le deuxième onglet : **"Contrôle Qualité"**.
2. En haut, choisissez le **Service** qui vous intéresse dans le menu déroulant.
3. Juste à côté, tapez le nombre de lignes que vous voulez tirer par question (j'ai mis 10 par défaut).
4. Vous allez voir la liste des questions du service. J'ai ajouté des petits badges de couleur pour voir tout de suite combien de réponses ont vraiment été remplies. Cochez les questions que vous voulez vérifier.
5. Cliquez sur **"Exporter Excel"**.
6. L'appli va générer un fichier `.xlsx` bien propre avec toutes les infos du patient et les réponses pour chaque question cochée. Pratique pour faire le point !
