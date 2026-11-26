from dataclasses import dataclass
from math import isfinite

import flet as ft
import sqlite3

from Test_map import afficher_carte

conn = sqlite3.connect("rando29.db")
cur = conn.cursor()

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


def req_sql(
    ville_flet=None,
    distancekm_flet=None,
    boucle_flet=None,
    difficulte_flet=None,
):
    conditions = []
    parametres = []

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
    elif boucle.casefold() == "sans boucle":
        conditions.append(
            "LOWER(TRIM(r.type_itineraire)) IN ('aller simple', 'aller-retour')"
        )
    elif boucle.casefold() not in ("", "tous", "peu importe"):
        conditions.append("LOWER(TRIM(r.type_itineraire)) = LOWER(TRIM(?))")
        parametres.append(boucle)

    difficulte = str(difficulte_flet or "").strip()
    if difficulte.casefold() not in ("", "toutes", "tous", "peu importe"):
        if difficulte.casefold() == "modérée":
            difficulte = "Moyen"
        conditions.append("r.difficulte = ? COLLATE NOCASE")
        parametres.append(difficulte)

    requete = """
        SELECT r.nom_itineraire, c.communes_nom, r.longueur, r.presentation,
               r.difficulte, r.altitude_min, r.altitude_max,
               r.denivele_negatif, r.denivele_positif, r.pratique,
               r.type_itineraire
        FROM randonnee AS r
        JOIN communes AS c ON r.communes_code = c.communes_code
    """
    if conditions:
        requete += " WHERE " + " AND ".join(conditions)

    cur.execute(requete, parametres)
    data = cur.fetchall()
    print(data)
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
    ville = ft.TextField(label="Ville", value="Saint-Brieuc")
    distance = ft.TextField(
        label="Distance maximale (km)",
        value="20",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    format_boucle = ft.Dropdown(
        label="Format",
        value="Peu importe",
        options=[
            ft.DropdownOption(key="Peu importe", text="Peu importe"),
            ft.DropdownOption(key="Boucle", text="Boucle"),
            ft.DropdownOption(key="Sans boucle", text="Sans boucle"),
        ],
    )
    difficulte = ft.Dropdown(
        label="Difficulté",
        value="Toutes",
        options=[
            ft.DropdownOption(key="Toutes", text="Toutes"),
            ft.DropdownOption(key="Facile", text="Facile"),
            ft.DropdownOption(key="Modérée", text="Modérée"),
            ft.DropdownOption(key="Difficile", text="Difficile"),
        ],
    )
    message_erreur = ft.Text(color=ft.Colors.RED)
        
    # Panneau de résultats : les cartes sont remplacées à chaque recherche.
    nombre_resultats = ft.Text()
    liste_resultats = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=10)

    def afficher_resultats(randonnees: list[Randonnee]) -> None:
        nombre_resultats.value = f"{len(randonnees)} randonnée(s) trouvée(s)"
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
                    on_click=lambda _event, selection=randonnee: afficher_carte(
                        page,
                        selection.nom,
                        selection.ville,
                        retour=lambda: afficher_recherche(page),
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
        if not randonnees:
            liste_resultats.controls.append(ft.Text("Aucune randonnée trouvée."))

    def afficher_recherche(_page: ft.Page) -> None:
        main(_page)

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

        RANDONNEES = FindRando(ville.value or '',distance_max,format_boucle.value,difficulte.value)
        #Lancement des fonctions de recherche et d'affichage
        afficher_resultats(RANDONNEES)
        page.update()

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
    afficher_resultats(FindRando(ville.value or '',float((distance.value or "").strip().replace(",", ".")),format_boucle.value,difficulte.value))
    page.update()


if __name__ == "__main__":
    ft.run(main)
