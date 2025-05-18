from src.transformation.transformation.electoral_transformer import ElectoralTransformer
from src.transformation.transformation.socio_eco_transformer import SocioEcoTransformer
from src.transformation.transformation.fusionner import Fusionner
from src.ingestion.ingest import run_ingestion
import pandas as pd, pathlib

CURATED  = pathlib.Path("data/curated"); CURATED.mkdir(parents=True, exist_ok=True)

def main():
    # Récupérer les données directement depuis l'ingestion
    data = run_ingestion()
    elections = data["elections"]
    socio_eco = data["socio_eco"]
    communes  = data["communes"]
    
    # Assurer la cohérence des types de données pour la colonne code_commune
    elections["code_commune"] = elections["code_commune"].astype(str)
    socio_eco["code_commune"] = socio_eco["code_commune"].astype(str)
    communes["code_commune"] = communes["code_commune"].astype(str)

    elections_tidy = ElectoralTransformer().transform(elections, communes)
    socio_tidy     = SocioEcoTransformer().transform(socio_eco)

    dataset        = Fusionner().transform(elections_tidy, socio_tidy)
    dataset.to_parquet(CURATED / "dataset.parquet")
    print("✅  Transformation terminée :", dataset.shape)
