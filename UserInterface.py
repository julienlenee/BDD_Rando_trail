from dataclasses import dataclass
from math import isfinite

import flet as ft
import sqlite3

from Test_map import afficher_carte

conn = sqlite3.connect("rando29.db")
cur = conn.cursor()

#Définition de la structure randonnée (reflet de notre table RANDONNEE in DB)
@dataclass(frozen=True)
class Randonnee:
    nom: str
    ville: str
    distance_km: float
    transports: tuple[str, ...]
    boucle: bool
    difficulte: str
    description: str = ""
    denivele_positif: int | None = None
    denivele_negatif: int | None = None
    altitude_min: int | None = None
    altitude_max: int | None = None

# Format les saisies utilisateur, execute la requète sql et retourne chaque ligne
def req_sql(ville_flet=None,distancekm_flet=None,boucle_flet=None,difficulte_flet=None):
    conditions = [] # stock les requetes des filtres récupérés
    parametres = []

    #------------------------------------------------ Formatage des saisies -----
    if ville_flet and str(ville_flet).strip():
        conditions.append("TRIM(c.communes_nom) = TRIM(?) COLLATE NOCASE")
        parametres.append(str(ville_flet).strip())

    if distancekm_flet is not None and str(distancekm_flet).strip():
        conditions.append("r.longueur <= ?")
        parametres.append(
            float(str(distancekm_flet).strip().replace(",", ".")) * 1000
        )

    boucle = str(boucle_flet or "").strip()
    if boucle.casefold() == "boucle":
        conditions.append("LOWER(TRIM(r.type_itineraire)) = 'boucle'")
    elif boucle.casefold() == "aller simple":
        conditions.append(
            "LOWER(TRIM(r.type_itineraire)) IN ('aller simple', 'aller-retour')"
        )
    elif boucle.casefold() not in ("","peu importe"):
        conditions.append("LOWER(TRIM(r.type_itineraire)) = LOWER(TRIM(?))")
        parametres.append(boucle)

    difficulte = str(difficulte_flet or "").strip()
    if difficulte.casefold() not in ("", "toutes"):
        conditions.append("r.difficulte = ? COLLATE NOCASE")
        parametres.append(difficulte)

    #Création de la requête
    requete = """
        SELECT r.nom_itineraire, c.communes_nom, r.longueur, r.presentation,
               r.difficulte, r.altitude_min, r.altitude_max,
               r.denivele_negatif, r.denivele_positif, r.pratique,
               r.type_itineraire
        FROM randonnee AS r
        JOIN communes AS c ON r.communes_code = c.communes_code
    """
    #Ajoute des conditions en fonction des filtre enregistrés dans condition
    if conditions:
        requete += " WHERE " + " AND ".join(conditions)

    cur.execute(requete, parametres)
    data = cur.fetchall()
    return data

def FindRando(ville1,distance1,format_boucle1,difficulte1):
    res = req_sql(ville1, distance1, format_boucle1, difficulte1) #Requete vers BDD en fonction des filtres

    randonnees = []
    for ligne in res: # Pour chaque ligne on recupère les variables
        nom,ville,distance,presentation,difficulte,altitude_min,altitude_max,denivele_negatif,denivele_positif,transport,type_itineraire = ligne

        transports = (transport,) if isinstance(transport, str) else tuple(transport or ()) #Gestion du format particulier

        randonnees.append(   # création d'une liste d'objet randonnée
            Randonnee(
                nom=nom,
                ville=ville.strip(),
                distance_km=float(distance) / 1000,
                transports=transports,
                boucle=(type_itineraire or "").strip().casefold() == "boucle",
                difficulte=difficulte or "Non renseignée",
                description=presentation or "",
                denivele_positif=denivele_positif,
                denivele_negatif=denivele_negatif,
                altitude_min=altitude_min,
                altitude_max=altitude_max,
            )
        )

    return randonnees

def main(page: ft.Page) -> None: #--------------------------------------------- MAIN -------------
    page.controls.clear()
    page.title = "Recherche de randonnées"
    page.padding = 0

    # Filtres de recherche avec des valeurs d'exemple modifiables.
    ville = ft.TextField(label="Ville", hint_text="Ex. Saint-Brieuc")
    distance = ft.TextField(label="Distance maximale (km)",hint_text="Ex. 20",keyboard_type=ft.KeyboardType.NUMBER)
    
    format_boucle = ft.Dropdown(label="Format",value="Peu importe",
        options=[
            ft.DropdownOption(key="Peu importe", text="Peu importe"),
            ft.DropdownOption(key="Boucle", text="Boucle"),
            ft.DropdownOption(key="Aller simple", text="Aller simple"),
        ],)
    difficulte = ft.Dropdown(label="Difficulté",value="Toutes",options=[
            ft.DropdownOption(key="Toutes", text="Toutes"),
            ft.DropdownOption(key="Facile", text="Facile"),
            ft.DropdownOption(key="Moyen", text="Moyen"),
            ft.DropdownOption(key="Difficile", text="Difficile"),
        ],)
    
    message_erreur = ft.Text(color=ft.Colors.RED)
        
    # Panneau de résultats : les cartes sont remplacées à chaque recherche par chaque ligne de la nouvelle liste randonnée
    nombre_resultats = ft.Text()
    liste_resultats = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

    def afficher_resultats(randonnees: list[Randonnee]) -> None: #Creer et affiche les widgets pour chaque ligne de la liste randonnee
        nombre_resultats.value = f"{len(randonnees)} randonnée(s) trouvée(s)"
        #Création d'un widget card pour chaque randonnée issue de la requête
        liste_resultats.controls = [
            ft.Card(
                content=ft.ListTile(
                    title=ft.Text(
                        randonnee.nom, size=18, weight=ft.FontWeight.BOLD
                    ),
                    subtitle=ft.Text(
                        f"{randonnee.ville} · {randonnee.distance_km:g} km · "
                        f"{', '.join(randonnee.transports)} · "
                        f"{'Boucle' if randonnee.boucle else 'Sans boucle'} · "
                        f"{randonnee.difficulte}"
                    ),
                    #Ajout d'une fonction bouton sur le widget lié à la page de visualisation de la carte
                    on_click=lambda _event, selection=randonnee: afficher_carte(
                        page,
                        selection.nom,
                        retour=lambda: afficher_recherche(page),# Gestion du bouton retour lié à la page de recherche
                        description=selection.description,
                        denivele_positif=selection.denivele_positif,
                        denivele_negatif=selection.denivele_negatif,
                        altitude_min=selection.altitude_min,
                        altitude_max=selection.altitude_max,
                    ),
                )
            )
            for randonnee in randonnees
        ]
        #Si aucune randonnée trouvée
        if not randonnees:
            liste_resultats.controls.append(ft.Text("Aucune randonnée trouvée."))

    def afficher_recherche(_page: ft.Page) -> None:
        main(_page)

#Vérifie le format des champs de saisies et lance la fonction req_sql et affiche les résultat
    def lancer_recherche(_event: ft.ControlEvent) -> None:
        try:
            distance_max = float((distance.value or "").strip().replace(",", "."))
        except ValueError:
            message_erreur.value = "Saisir une distance valide, par exemple 15."
            page.update()
            return
        
        if not isfinite(distance_max) or distance_max <= 0:
            message_erreur.value = "La distance doit être un nombre positif."
            page.update()
            return

        message_erreur.value = ""
        #Si pas de problème, on lance la requète vers la BDD
        RANDONNEES = FindRando(ville.value or '',distance_max,format_boucle.value,difficulte.value)
        #Lancement des fonctions de recherche et d'affichage
        afficher_resultats(RANDONNEES)
        page.update()

    #Structuration de la colonne d'affichage des filtres
    filtres = ft.Column(
        controls=[
            ft.Text("Filtres de recherche", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Choisis tes critères pour trouver une randonnée."),
            ville,
            distance,
            format_boucle,
            difficulte,
            message_erreur,
            ft.FilledButton(
                content=ft.Text("Lancer la recherche"),
                icon=ft.Icons.SEARCH,
                on_click=lancer_recherche,
                expand=True,
            ),
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
    )
    #Ajout de tous les widgets créés et sctructuration sur la page
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Randonnées disponibles",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                nombre_resultats,
                                liste_resultats,
                            ],
                            expand=True,
                            spacing=12,
                        ),
                        expand=True,
                        padding=24,
                    ),
                    ft.Container(width=1, bgcolor="#DDDDDD"),
                    ft.Container(content=filtres, width=360, padding=24),
                ],
                expand=True,
                spacing=0,
            ),
        )
    )
    #affichage des résultats une première fois
    dist = float(distance.value.strip().replace(",", ".")) if distance.value else None 
    afficher_resultats(FindRando(ville.value or '',dist,format_boucle.value,difficulte.value))
    page.update()


if __name__ == "__main__":
    ft.run(main)
