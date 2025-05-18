-- Schéma SQL pour POC PREDICTION ÉLECTORALE

-- Table des régions (dimension)
CREATE TABLE IF NOT EXISTS dim_region (
  region_id SERIAL PRIMARY KEY,
  region_name VARCHAR(100) NOT NULL
);

-- Table des élections (dimension)
CREATE TABLE IF NOT EXISTS dim_election (
  election_id SERIAL PRIMARY KEY,
  year INT NOT NULL,
  election_type VARCHAR(50) DEFAULT 'municipal'
);

-- Table des mesures socio-économiques (fait)
CREATE TABLE IF NOT EXISTS fact_socio_economics (
  fact_id SERIAL PRIMARY KEY,
  region_id INT REFERENCES dim_region(region_id),
  election_id INT REFERENCES dim_election(election_id),
  unemployment_rate DECIMAL(5,2),
  median_income DECIMAL(10,2),
  crime_rate DECIMAL(7,2),
  population_density DECIMAL(7,2),
  turnout_rate DECIMAL(5,2)
);

-- Table des résultats électoraux (fait)
CREATE TABLE IF NOT EXISTS fact_election_results (
  result_id SERIAL PRIMARY KEY,
  region_id INT REFERENCES dim_region(region_id),
  election_id INT REFERENCES dim_election(election_id),
  vote_share_A DECIMAL(5,2),
  vote_share_B DECIMAL(5,2),
  vote_share_C DECIMAL(5,2)
);
