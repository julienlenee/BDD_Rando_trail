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


def req_sql(ville_flet=None,distancekm_flet=None,transports_flet=None,boucle_flet=None,difficulte_flet=None):
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

    transport = str(transports_flet or "").strip()
    if transport.casefold() not in ("", "tous", "peu importe"):
        if transport.casefold() in ("à pied", "pédestre"):
            conditions.append("r.pratique = ?")
            parametres.append("Pédestre")
        elif transport.casefold() in ("vélo", "à vélo"):
            conditions.append("r.pratique IN (?, ?)")
            parametres.extend(("Vélo", "VTT"))
        elif transport.casefold() in ("cheval", "à cheval"):
            conditions.append("r.pratique = ?")
            parametres.append("Equestre")
        else:
            conditions.append("r.pratique = ?")
            parametres.append(transport)

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

res = req_sql(None,40,"Pédestre","aller simple","Difficile")
'''count=0
for i in res:
    count+=1
    print(i)
    print(count)
'''

randonnees = []

for ligne in res:
    (
        nom,
        ville,
        distance,
        presentation,
        difficulte,
        altitude_min,
        altitude_max,
        denivele_negatif,
        denivele_positif,
        transport,
        type_itineraire,
    ) = ligne

    transports = (
        (transport,) if isinstance(transport, str) else tuple(transport or ())
    )

    randonnees.append(
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

RANDONNEES_EXEMPLE = tuple(randonnees)
'''
# Randonnées fictives utilisées comme exemples dans l'interface.
RANDONNEES_EXEMPLE = (
    Randonnee(
        "Tour du port du Légué",
        "Saint-Brieuc",
        5.2,
        ("À pied", "Vélo"),
        True,
        "Facile",
        "Balade d'exemple autour du port et des sentiers de Saint-Brieuc.",
        75,
        -75,
        4,
        55,
    ),
    Randonnee(
        "Balade des Rosaires",
        "Plérin",
        8.4,
        ("À pied", "Cheval"),
        True,
        "Facile",
        "Découverte des plages et du littoral de Plérin.",
        52,
        -50,
        0,
        45,
    ),
    Randonnee(
        "Boucle du Gouët",
        "Ploufragan",
        14.0,
        ("Vélo", "Cheval"),
        True,
        "Modérée",
        "Parcours vallonné autour de la vallée du Gouët.",
        185,
        -185,
        15,
        145,
    ),
    Randonnee(
        "Sentier côtier de Binic",
        "Binic",
        12.5,
        ("À pied",),
        False,
        "Modérée",
        "Suivez le sentier côtier et ses points de vue.",
        140,
        -140,
        0,
        80,
    ),
    Randonnee(
        "Chemins de campagne",
        "Plélo",
        18.0,
        ("Cheval",),
        True,
        "Difficile",
        "Chemins de campagne sur les hauteurs de Plélo.",
        230,
        -230,
        40,
        190,
    ),
    Randonnee(
        "Circuit de la baie",
        "Langueux",
        9.8,
        ("À pied", "Vélo"),
        False,
        "Facile",
        "Balade d'exemple entre la baie et les chemins de Langueux.",
        62,
        -60,
        0,
        48,
    ),
)
'''

def rechercher_randonnees(
    ville: str,
    distance_max: float,
    transport: str,
    format_boucle: str,
    difficulte: str,
) -> list[Randonnee]:
    ville_recherchee = ville.strip().casefold()
    return [
        randonnee
        for randonnee in RANDONNEES_EXEMPLE
        if (not ville_recherchee or ville_recherchee in randonnee.ville.casefold())
        and randonnee.distance_km <= distance_max
        and (transport == "Tous" or transport in randonnee.transports)
        and (
            format_boucle == "Peu importe"
            or randonnee.boucle == (format_boucle == "Boucle")
        )
        and (difficulte == "Toutes" or randonnee.difficulte == difficulte)
    ]


def main(page: ft.Page) -> None:
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
    transport = ft.Dropdown(
        label="Moyen de transport",
        value="Tous",
        options=[
            ft.DropdownOption(key="Tous", text="Tous"),
            ft.DropdownOption(key="Vélo", text="À vélo"),
            ft.DropdownOption(key="À pied", text="À pied"),
            ft.DropdownOption(key="Cheval", text="À cheval"),
        ],
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
            message_erreur.value = "Saisis une distance valide, par exemple 15."
            page.update()
            return

        if not isfinite(distance_max) or distance_max <= 0:
            message_erreur.value = "La distance doit être un nombre positif."
            page.update()
            return

        message_erreur.value = ""
        #Lancement des fonctions de recherche et d'affichage
        afficher_resultats(
            rechercher_randonnees(
                ville.value or "",
                distance_max,
                transport.value or "Tous",
                format_boucle.value or "Peu importe",
                difficulte.value or "Toutes",
            )
        )
        page.update()

    filtres = ft.Column(
        controls=[
            ft.Text("Filtres de recherche", size=22, weight=ft.FontWeight.BOLD),
            ft.Text("Choisis tes critères pour trouver une randonnée."),
            ville,
            distance,
            transport,
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
    afficher_resultats(list(RANDONNEES_EXEMPLE))
    page.update()


if __name__ == "__main__":
    ft.run(main)
