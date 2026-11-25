CREATE TABLE communes (
    communes_code TEXT PRIMARY KEY,
    communes_nom TEXT
);

CREATE TABLE randonnee (
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

CREATE TABLE trace (
    trace_uuid TEXT PRIMARY KEY,
    geometry TEXT,
    FOREIGN KEY (trace_uuid) REFERENCES randonnee(rando_uuid)
);