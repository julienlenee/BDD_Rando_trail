import csv
from io import StringIO
from itertools import islice

import requests


API_URL = (
    "https://datarmor.cotesdarmor.fr/data-fair/api/v1/datasets/"
    "itineraires-de-randonnee-inscrits-au-pdipr-du-departement-des-cotes-darmor/raw"
)


def main() -> None:
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise SystemExit(f"Erreur lors de l'appel à l'API : {error}") from error

    content_type = response.headers.get("Content-Type", "")
    if "text/csv" not in content_type.lower():
        raise SystemExit(f"Format inattendu renvoyé par l'API : {content_type}")

    itineraires = csv.DictReader(StringIO(response.text))
    if not itineraires.fieldnames or "nom_itineraire" not in itineraires.fieldnames:
        raise SystemExit("Le CSV reçu ne contient pas la colonne « nom_itineraire ».")

    print("Premiers itinéraires récupérés :")
    for itineraire in islice(itineraires, 5):
        nom = itineraire.get("nom_itineraire") or "(sans nom)"
        commune = itineraire.get("communes_nom") or "commune inconnue"
        print(f"- {nom} — {commune}")


if __name__ == "__main__":
    main()
