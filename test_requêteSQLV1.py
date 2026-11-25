import sqlite3

conn = sqlite3.connect("rando29.db")
cur = conn.cursor()

def req_sql(ville_flet, distancekm_flet, transports_flet, boucle_flet, difficulte_flet):
    
    cur.execute("""
                SELECT r.nom_itineraire,c.communes_nom,r.longueur,r.presentation,r.difficulte,r.altitude_min,r.altitude_max,r.denivele_negatif,r.denivele_positif,r.pratique,r.type_itineraire FROM randonnee AS r
                JOIN communes AS c
                ON r.communes_code = c.communes_code
                WHERE c.communes_nom = ? AND r.longueur <= ? 
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