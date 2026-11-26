# Rando Trail

Application de recherche de randonnées dans les Côtes-d'Armor, avec affichage des parcours sur une carte.

## Fichiers du projet

- `main.py` : lance l'application du projet.
- `UserInterface.py` : recherche les randonnées dans la base et affiche les filtres et résultats (première fenetre).
- `Test_map.py` : récupère les traces, convertit leurs coordonnées et affiche la carte (seconde fentre).
- `rando29.db` : base SQLite contenant les communes, randonnées et traces.
- `base_test.sql` : définition SQL des tables de la base.
- `testdb.py` : crée les tables si elles n'existent pas.
- `test.py` : télécharge les randonnées depuis l'API Data Armor et recharge la base. **Ce script vide d'abord les tables existantes.**
- `requirements.txt` : dépendances Python de l'application.
- `.gitignore` : exclut l'environnement virtuel `.venv`.

## Utilisation

La base `rando29.db` est fournie. Pour la recréer et importer les données en ligne, lance `testdb.py`, puis `test.py`. **L'import efface les données actuelles** et nécessite une connexion Internet.

## Petit dictionnaire

- **BDD** : base de données ; ici, le fichier `rando29.db`.
- **SQLite** : système qui stocke et interroge la base dans un fichier.
- **SQL** : langage utilisé pour créer les tables et rechercher les randonnées.
- **Commune** : ville associée à une randonnée.
- **Trace** : suite de coordonnées qui dessine un parcours sur la carte.
- **UUID** : identifiant unique d'une randonnée ou d'une trace.
- **`?` dans une requête** : emplacement d'une valeur transmise séparément à SQL.
- **Lambert-93 / WGS84** : systèmes de coordonnées ; la trace est convertie en WGS84 pour l'afficher sur la carte.
- **Tuile** : petite image cartographique chargée pour composer le fond de carte.
