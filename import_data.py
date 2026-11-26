import json
import requests
import sqlite3

URL = "https://datarmor.cotesdarmor.fr/data-fair/api/v1/datasets/itineraires-de-randonnee-inscrits-au-pdipr-du-departement-des-cotes-darmor/lines"
TAILLE_PAGE = 100

conn = sqlite3.connect("rando29.db")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

page = 1
total_recupere = 0

cur.execute("DELETE FROM trace;")
cur.execute("DELETE FROM randonnee")
cur.execute("DELETE FROM communes")
conn.commit()

while True:
    reponse = requests.get(
        URL,
        params={"page": page, "size": TAILLE_PAGE},
        timeout=15,
    )
    reponse.raise_for_status()
    donnees = reponse.json()

    data = donnees.get("results", [])
    if not data:
        break

    for ligne in data:
        code_commune = ligne.get("communes_code")
        nom_commune = ligne.get("communes_nom")
        
        real_code = code_commune.split(",")
        real_nom = nom_commune.split(",")
        rando_uuid = ligne.get("uuid")

        if len(real_code) == len(real_nom):
            for code_commune, nom_commune in zip(real_code, real_nom):
                cur.execute(
                    "INSERT OR IGNORE INTO communes (communes_code, communes_nom) VALUES (?, ?)",
                    (code_commune, nom_commune),
                )
        else:
            print(f"Erreur : le nombre de codes et de noms de communes ne correspond pas pour la ligne {ligne.get('uuid')}")
      
        cur.execute(
            """
            INSERT OR IGNORE INTO randonnee (
                rando_uuid, nom_itineraire, longueur, presentation, difficulte,
                altitude_min, altitude_max, denivele_negatif, denivele_positif,
                pratique, type_itineraire, theme, depart, geo_depart, communes_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rando_uuid,
                ligne.get("nom_itineraire"),
                ligne.get("longueur"),
                ligne.get("presentation"),
                ligne.get("difficulte"),
                ligne.get("altitude_min"),
                ligne.get("altitude_max"),
                ligne.get("denivele_negatif"),
                ligne.get("denivele_positif"),
                ligne.get("pratique"),
                ligne.get("type_itineraire"),
                ligne.get("themes"),
                ligne.get("depart"),
                ligne.get("_geopoint"),
                code_commune,
            ),
        )
        if rando_uuid and ligne.get("geometry"):
            cur.execute(
                "INSERT OR IGNORE INTO trace (trace_uuid, geometry) VALUES (?, ?)",
                (rando_uuid, ligne.get("geometry")),
            )

    total_recupere += len(data)
    print(f"Page {page} traitée ({total_recupere} lignes vues)")
    page += 1

conn.commit()
conn.close()
print("Import terminé.")
