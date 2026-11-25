import sqlite3

conn = sqlite3.connect("rando29.db")
cur = conn.cursor()

def req_sql(ville_flet, distancekm_flet, transports_flet, boucle_flet, difficulte_flet):
    
    cur.execute("""
                SELECT r.nom_itineraire,c.communes_nom,r.longueur,r.presentation,r.difficulte,r.altitude_min,r.altitude_max,r.denivele_negatif,r.denivele_positif,r.pratique,r.type_itineraire FROM randonnee AS r
                JOIN communes AS c
                ON r.communes_code = c.communes_code
                WHERE c.communes_nom = ? AND r.longueur <= ?
                AND r.difficulte = ? AND LOWER(r.type_itineraire) = LOWER(?) AND r.pratique = ?
            """,
            (
                ville_flet,
                distancekm_flet*1000,
                difficulte_flet,
                boucle_flet,
                transports_flet,
            ),
    )
    data = cur.fetchall()
    print(data)

req_sql("PERROS-GUIREC",9,"Pédestre","Boucle","Facile")

'''def req_sql(
    ville_flet=None,
    distancekm_flet=None,
    transports_flet=None,
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

    cur.execute(requete, parametres)'''