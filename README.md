# BDD_Rando_trail
Projet universitaire de base de données SQL.

## Tester l'appel à l'API

Le script `main.py` interroge l'API des itinéraires de randonnée des Côtes-d'Armor
avec une requête HTTP `GET`. Cette URL renvoie un fichier CSV : le script en lit
et affiche les cinq premiers itinéraires.

Crée un environnement virtuel, installe la dépendance, puis lance le script depuis
PowerShell dans le dossier du projet :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Le script vérifie le statut HTTP avant de lire la réponse. En cas d'erreur réseau
ou HTTP, il affiche un message explicite.

## Carte interactive des Côtes-d'Armor

`Test_map.py` ouvre une fenêtre Flet native avec une carte interactive centrée
sur Saint-Brieuc. Elle affiche le fond Plan IGN v2 de la Géoplateforme, un
itinéraire schématique et ses étapes :

```powershell
python -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\Test_map.py
```

La carte permet de zoomer et de se déplacer. L'itinéraire est illustratif et ne
représente pas un sentier vérifié.
git config --global user.name "Ton Nom"
git config --global user.email "ton.email@exemple.com"