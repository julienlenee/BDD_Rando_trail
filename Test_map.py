import flet as ft
import flet_map as ftm
import pandas as pd


# Définition du centre de la carte et étapes de l'itinéraire d'exemple ------------------------------------
CENTRE = ftm.MapLatitudeLongitude(latitude=48.5142, longitude=-2.7657)
ITINERAIRE = pd.DataFrame(
    [
        ("Départ / arrivée", 48.5142, -2.7657),
        ("Étape 1", 48.5210, -2.7820),
        ("Étape 2", 48.5290, -2.7690),
        ("Étape 3", 48.5260, -2.7490),
    ],
    columns=("étape", "latitude", "longitude"),
)
#---------------------------------------------------------------------------------------------------------

# Flet remplace {z}, {x} et {y} par le zoom et les coordonnées de chaque tuile.
IGN_WMTS_URL = (
    "https://data.geopf.fr/wmts?"
    "SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
    "&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2"
    "&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM_0_19"
    "&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}"
)


def main(page: ft.Page) -> None:
    page.title = "Randonnée dans les Côtes-d'Armor"

    # Convertit les lignes du tableau en coordonnées attendues par la carte.
    coordinates = [
        ftm.MapLatitudeLongitude(
            latitude=etape["latitude"],
            longitude=etape["longitude"],
        )
        for _, etape in ITINERAIRE.iterrows()
    ]
    # Ajoute le point de départ à la fin pour fermer la boucle.
    coordinates.append(coordinates[0])

    # Les couches sont dessinées dans l'ordre : fond, tracé, puis marqueurs.
    carte = ftm.Map(
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
            ftm.PolylineLayer(
                polylines=[
                    ftm.PolylineMarker(
                        coordinates=coordinates,
                        color=ft.Colors.RED,
                        border_color=ft.Colors.RED,
                        border_stroke_width=4,
                    )
                ]
            ),
            ftm.MarkerLayer(
                markers=[
                    ftm.Marker(
                        coordinates=ftm.MapLatitudeLongitude(
                            latitude=etape["latitude"],
                            longitude=etape["longitude"],
                        ),
                        content=ft.Icon(
                            ft.Icons.LOCATION_ON,
                            color=ft.Colors.RED,
                            size=32,
                        ),
                    )
                    for _, etape in ITINERAIRE.iterrows()
                ]
            ),
        ],
    )

    # Panneau latéral listant les étapes et leurs coordonnées.
    etapes = ft.Column(
        controls=[
            ft.Text("Itinéraire d'exemple", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Boucle schématique, non vérifiée sur le terrain."),
            *[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED),
                    title=ft.Text(etape["étape"]),
                    subtitle=ft.Text(
                        f'{etape["latitude"]:.4f}, {etape["longitude"]:.4f}'
                    ),
                )
                for _, etape in ITINERAIRE.iterrows()
            ],
        ],
        spacing=8,
        width=280,
        scroll=ft.ScrollMode.AUTO,
    )

    # Place la liste à côté de la carte dans la fenêtre.
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Row(
                controls=[
                    ft.Container(content=etapes, padding=16),
                    ft.Container(content=carte, expand=True),
                ],
                expand=True,
                spacing=0,
            ),
        )
    )


if __name__ == "__main__":
    # Lance l'application dans une fenêtre Flet.
    ft.run(main)
