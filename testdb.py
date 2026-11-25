import sqlite3

sql_creation = """
CREATE TABLE IF NOT EXISTS communes (
    communes_code TEXT PRIMARY KEY,
    communes_nom TEXT
);

CREATE TABLE IF NOT EXISTS randonnee (
    rando_uuid TEXT PRIMARY KEY,
    nom_itineraire TEXT,
    longueur INTEGER,
    presentation TEXT,
    difficulte TEXT,
    altitude_min INTEGER,
    altitude_max INTEGER,
    denivele_negatif INTEGER,
    denivele_positif INTEGER,
    pratique TEXT,
    type_itineraire TEXT,
    theme TEXT,
    depart TEXT,
    geo_depart TEXT,
    communes_code TEXT,
    FOREIGN KEY (communes_code) REFERENCES communes(communes_code)
);

CREATE TABLE IF NOT EXISTS trace (
    trace_uuid TEXT PRIMARY KEY,
    geometry TEXT,
    FOREIGN KEY (trace_uuid) REFERENCES randonnee(rando_uuid)
);
"""

conn = sqlite3.connect("rando29.db")
cur = conn.cursor()

cur.executescript(sql_creation)
conn.commit()
conn.close()