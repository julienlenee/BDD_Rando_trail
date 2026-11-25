# BDD_Rando_trail
Projet universitaire de base de données SQL.

## Lancer l'application

Crée un environnement virtuel, installe la dépendance, puis lance le script depuis
PowerShell dans le dossier du projet :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\main.py
```

`main.py` ouvre l'interface Flet de `UserInterface.py`. Les randonnées d'exemple
sont listées à gauche et les filtres sont à droite. Clique sur une randonnée
pour ouvrir sa vue cartographique dans la même fenêtre ; le bouton « Retour »
revient à la recherche.

Les randonnées et le tracé affiché sont des exemples à remplacer par les données
réelles.
git config --global user.name "Ton Nom"
git config --global user.email "ton.email@exemple.com"