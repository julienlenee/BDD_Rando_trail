import os
from pathlib import Path

import requests


ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
ACCESS_TOKEN = pk.eyJ1IjoiYmFzaWxlMjQ2IiwiYSI6ImNtd3VuNTZ5YTAwY3IyeHIwazByY25tdm4ifQ.jmaYe8TcekWicAzl1K05ZA
if not ACCESS_TOKEN:
    raise SystemExit("Définis la variable d'environnement MAPBOX_ACCESS_TOKEN.")

url = (
    "https://api.mapbox.com/styles/v1/mapbox/streets-v12/"
    "static/-3.0,48.2,8/1000x700"
)

try:
    response = requests.get(
        url,
        params={"access_token": ACCESS_TOKEN, "format": "png"},
        timeout=30,
    )
    response.raise_for_status()
except requests.exceptions.RequestException as error:
    raise SystemExit(f"Erreur lors de l'appel à Mapbox : {error}") from error

image_path = Path(__file__).with_name("bretagne.png")
image_path.write_bytes(response.content)
print(f"Carte enregistrée dans : {image_path}")