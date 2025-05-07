-- Création des tables
CREATE TABLE IF NOT EXISTS elections (
    id SERIAL PRIMARY KEY,
    annee INTEGER,
    type_election VARCHAR(100),
    departement VARCHAR(3),
    commune VARCHAR(100),
    nb_inscrits INTEGER,
    nb_votants INTEGER,
    nb_exprimes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emploi (
    id SERIAL PRIMARY KEY,
    annee INTEGER,
    departement VARCHAR(3),
    commune VARCHAR(100),
    categorie VARCHAR(50),
    nb_demandeurs INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS securite (
    id SERIAL PRIMARY KEY,
    annee INTEGER,
    departement VARCHAR(3),
    commune VARCHAR(100),
    type_delit VARCHAR(100),
    nb_faits INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Création des index
CREATE INDEX idx_elections_commune ON elections(commune);
CREATE INDEX idx_emploi_commune ON emploi(commune);
CREATE INDEX idx_securite_commune ON securite(commune);