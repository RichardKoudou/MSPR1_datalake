from src.ingestion.loading import elections_loader, socio_eco_loader, communes_loader
import yaml

_LOADERS = {
    "elections": (elections_loader.ElectionsAPILoader,
                  elections_loader.ElectionsFakeLoader),
    "socio_eco": (socio_eco_loader.SocioEcoAPILoader,
                  socio_eco_loader.SocioEcoFakeLoader),
    "communes":  (communes_loader.CommunesLoader,
                  communes_loader.CommunesLoader),   # même classe pour les 2 modes
}

def run_ingestion():
    """
    Lance l'ingestion des données
    """
    # Charger la configuration
    cfg = yaml.safe_load(open("config.yml"))
    
    results = {}
    for dataset, (APILoader, FakeLoader) in _LOADERS.items():
        # Récupérer la configuration spécifique au dataset
        dataset_cfg = cfg.get("ingestion", {}).get(dataset, {})
        
        print(f"Chargement des données {dataset}...")
        if cfg["mode"] == "prod":
            loader = APILoader(dataset_cfg)
        else:
            loader = FakeLoader(dataset_cfg)

        # Charger les données
        data = loader.load()
        results[dataset] = data
        print(f"Données {dataset} chargées: {len(data)} lignes")

    return results