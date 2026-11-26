from collections.abc import Callable

import sqlite3
import re
from pyproj import Transformer 

import flet as ft
import flet_map as ftm
import pandas as pd

CENTRE = ftm.MapLatitudeLongitude(latitude=48.5142, longitude=-2.7657)

IGN_WMTS_URL = (
    "https://data.geopf.fr/wmts?"
    "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
    "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"
    "&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM_0_19"
    "&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
)

#conversion des points projetées lambert 93 en latitude longitude demandé par flet
VERS_WGS84 = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)

#fonction pour récupérer les trace dans la base à partir du trajet sélectionné
def recup_trace(nom:str,ville:str| None = None)-> tuple[str | None, str | None]:
    connection = sqlite3.connect("rando29.db")
    cur = connection.cursor()
    
    if ville :
        cur.execute("""
                SELECT r.rando_uuid,t.geometry FROM randonnee AS r
                JOIN communes AS c ON r.communes_code = c.communes_code
                LEFT JOIN trace AS t ON t.trace_uuid = r.rando_uuid
                WHERE TRIM(r.nom_itineraire) = TRIM(?)
                AND TRIM(c.communes_nom) = TRIM(?)
                LIMIT 1
                """,
                (nom,ville),
                )
    else :
        cur.execute("""
                SELECT r.rando_uuid,t.geometry FROM randonnee AS r
                JOIN trace AS t ON t.trace_uuid = r.rando_uuid
                WHERE TRIM(r.nom_itineraire) = TRIM(?)
                LIMIT 1
                """,
                (nom),
                )
    data = cur.fetchone()
    connection.close()
    if not data:
        return None, None
    return data[0], data[1]

#fonction pour convertir l'attribut geometry en liste de point Latitude Longitude
def geometry_vers_points(geometry: str | None) -> list[ftm.MapLatitudeLongitude]:
    if not geometry:
        return []

    match = re.search(r"LINESTRING\s*\((.+)\)", geometry.strip(), re.IGNORECASE)
    if not match:
        return []

    points: list[ftm.MapLatitudeLongitude] = []
    for paire in match.group(1).split(","):
        morceaux = paire.strip().split()
        if len(morceaux) >= 2:
            x, y = float(morceaux[0]), float(morceaux[1])
            lon, lat = VERS_WGS84.transform(x, y)
            points.append(ftm.MapLatitudeLongitude(latitude=lat, longitude=lon))

    return points   



def afficher_carte(
    page: ft.Page,
    nom_randonnee: str | None = None,
    ville: str | None = None,
    retour: Callable[[], None] | None = None,
    *,
    description: str | None = None,
    denivele_positif: int | float | None = None,
    denivele_negatif: int | float | None = None,
    altitude_min: int | float | None = None,
    altitude_max: int | float | None = None,
) -> None:
    page.controls.clear()
    page.padding = 0
    page.title = nom_randonnee or "Randonnée dans les Côtes-d'Armor"

    _, geometry = recup_trace(nom_randonnee, ville) if nom_randonnee else (None, None)
    points_trace = geometry_vers_points(geometry)

    if points_trace:
        carte_widget: ft.Control = ftm.Map(
            expand=True,
            initial_center=points_trace[0],
            initial_zoom=13,
            layers=[
                ftm.TileLayer(
                    url_template=IGN_WMTS_URL,
                    user_agent_package_name="rando-trail/1.0",
                    max_zoom=19,
                    on_image_error=lambda event: print(
                        f"Erreur de chargement d'une tuile IGN : {event.data}"
                    ),
                ),
                ftm.SimpleAttribution(text="© IGN - Géoplateforme"),
                ftm.PolylineLayer(
                    polylines=[
                        ftm.PolylineMarker(
                            coordinates=points_trace,
                            color=ft.Colors.RED,
                            border_color=ft.Colors.RED,
                            border_stroke_width=4,
                        )
                    ]
                ),
                ftm.MarkerLayer(
                    markers=[
                        ftm.Marker(
                            coordinates=points_trace[0],
                            content=ft.Icon(
                                ft.Icons.LOCATION_ON,
                                color=ft.Colors.GREEN,
                                size=32,
                            ),
                        ),
                        ftm.Marker(
                            coordinates=points_trace[-1],
                            content=ft.Icon(
                                ft.Icons.FLAG,
                                color=ft.Colors.RED,
                                size=30,
                            ),
                        ),
                    ]
                ),
            ],
        )
        resume_trace = [
            ft.Text("Résumé du tracé", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(f"Points enregistrés : {len(points_trace)}"),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.GREEN),
                title=ft.Text("Départ"),
                subtitle=ft.Text(
                    f"{points_trace[0].latitude:.4f}, {points_trace[0].longitude:.4f}"
                ),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED),
                title=ft.Text("Arrivée"),
                subtitle=ft.Text(
                    f"{points_trace[-1].latitude:.4f}, {points_trace[-1].longitude:.4f}"
                ),
            ),
        ]
    else:
        carte_fond = ftm.Map(
            expand=True,
            initial_center=CENTRE,
            initial_zoom=12,
            layers=[
                ftm.TileLayer(
                    url_template=IGN_WMTS_URL,
                    user_agent_package_name="rando-trail/1.0",
                    max_zoom=19,
                    on_image_error=lambda event: print(
                        f"Erreur de chargement d'une tuile IGN : {event.data}"
                    ),
                ),
                ftm.SimpleAttribution(text="© IGN - Géoplateforme"),
            ],
        )
        carte_widget = ft.Stack(
            expand=True,
            controls=[
                carte_fond,
                ft.Container(
                    content=ft.Text(
                        "Cette trace n'est pas disponible",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
        )
        resume_trace = [
            ft.Text("Résumé du tracé", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Cette trace n'est pas disponible"),
        ]

    description_affichee = description.strip() if description else "Non renseignée",
            
    etapes = ft.Column(
        controls=[
            ft.Text("Description", weight=ft.FontWeight.BOLD),
            ft.Card(content=ft.Container(ft.Column(ft.Text(description_affichee),scroll=ft.ScrollMode.AUTO),),),
            ft.Text(
                f"Dénivelé positif : {denivele_positif:+g} m"
                if denivele_positif is not None
                else "Dénivelé positif : Non renseigné"
            ),
            ft.Text(
                f"Dénivelé négatif : {denivele_negatif:g} m"
                if denivele_negatif is not None
                else "Dénivelé négatif : Non renseigné"
            ),
            ft.Text(
                f"Altitude minimale : {altitude_min:g} m"
                if altitude_min is not None
                else "Altitude minimale : Non renseignée"
            ),
            ft.Text(
                f"Altitude maximale : {altitude_max:g} m"
                if altitude_max is not None
                else "Altitude maximale : Non renseignée"
            ),
            *resume_trace,
        ],
        spacing=8,
        width=280,
        scroll=ft.ScrollMode.AUTO,
    )

    bouton_retour = (
        ft.FilledButton(
            content=ft.Text("Retour"),
            icon=ft.Icons.ARROW_BACK,
            width=120,
            on_click=lambda _event: retour(),
        )
        if retour is not None
        else ft.Container(width=120)
    )
    entete = ft.Row(
        controls=[
            bouton_retour,
            ft.Container(
                content=ft.Text(page.title, size=22, weight=ft.FontWeight.BOLD),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
            ft.Container(width=120),
        ],
        spacing=0,
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Container(content=entete, padding=16),
                    ft.Row(
                        controls=[
                            ft.Container(content=etapes, padding=16),
                            ft.Container(content=carte_widget, expand=True),
                        ],
                        expand=True,
                        spacing=0,
                    ),
                ],
                expand=True,
                spacing=0,
            ),
        )
    )
    page.update()

def main(page: ft.Page) -> None:
    afficher_carte(page)


if __name__ == "__main__":
    # Lance l'application dans une fenêtre Flet.
    ft.run(main)
