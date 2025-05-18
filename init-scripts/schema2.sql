-- Création de la base de données
CREATE DATABASE IF NOT EXISTS election_prediction;
USE election_prediction;

-- Table des communes
CREATE TABLE communes (
    commune_id INT PRIMARY KEY,
    nom_commune VARCHAR(100) NOT NULL,
    population INT NOT NULL,
    departement INT NOT NULL,
    CONSTRAINT chk_population CHECK (population > 0),
    CONSTRAINT chk_departement CHECK (departement BETWEEN 1 AND 95)
);

-- Table des données socio-économiques
CREATE TABLE donnees_socio_economiques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commune_id INT NOT NULL,
    annee INT NOT NULL,
    taux_chomage DECIMAL(5,2) NOT NULL,
    revenu_median DECIMAL(10,2) NOT NULL,
    taux_criminalite DECIMAL(5,2) NOT NULL,
    niveau_education DECIMAL(5,2) NOT NULL,
    densite_population DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (commune_id) REFERENCES communes(commune_id),
    CONSTRAINT chk_annee CHECK (annee BETWEEN 2000 AND 2100),
    CONSTRAINT chk_taux_chomage CHECK (taux_chomage BETWEEN 0 AND 100),
    CONSTRAINT chk_niveau_education CHECK (niveau_education BETWEEN 0 AND 100),
    UNIQUE KEY unique_commune_annee (commune_id, annee)
);

-- Table des résultats électoraux
CREATE TABLE resultats_elections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commune_id INT NOT NULL,
    annee INT NOT NULL,
    parti VARCHAR(50) NOT NULL,
    pourcentage_votes DECIMAL(5,2) NOT NULL,
    taux_participation DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (commune_id) REFERENCES communes(commune_id),
    CONSTRAINT chk_pourcentage_votes CHECK (pourcentage_votes BETWEEN 0 AND 100),
    CONSTRAINT chk_taux_participation CHECK (taux_participation BETWEEN 0 AND 100)
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_commune_annee ON donnees_socio_economiques(commune_id, annee);
CREATE INDEX idx_election_commune_annee ON resultats_elections(commune_id, annee);