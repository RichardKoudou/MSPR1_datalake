import pandas as pd
from src.etl.data_collector import DataCollector
from src.etl.data_transformer import DataTransformer

def main():
    """
    Main function to execute the data collection, transformation, prediction, and visualization.
    """

    # Initialisation du collecteur de données
    collector = DataCollector()

    # Liste des URLs pour la collecte de données
    urls = [
        "https://www.data.gouv.fr/fr/pages/donnees-emploi/",
        "https://www.data.gouv.fr/fr/pages/donnees-elections/",
        "https://www.data.gouv.fr/fr/pages/donnees-securite/"
    ]

    # Vérification de l'existence des données
    if not collector.check_data_exists():
        print("Aucune donnée existante trouvée. Démarrage de la collecte des données...")
        collector.collect_all_data(urls)
        print("Collecte des données terminée.")
    else:
        print("Les données existent déjà dans le stockage.")
        # Lancement du processus ETL
        print("Démarrage du processus ETL...")
        # Initialisation du transformateur de données
        transformer = DataTransformer()
        try:
            # Chargement des données
            election_data = pd.read_csv('data/csv/election_data.csv')  # Ajustez le chemin selon votre structure
            socioeconomic_data = pd.read_csv('data/raw/socioeconomic_data.csv')  # Ajustez le chemin selon votre structure
            # Nettoyage des données
            clean_election_data = transformer.clean_election_data(election_data)
            clean_socioeconomic_data = transformer.clean_socioeconomic_data(socioeconomic_data)
            # Fusion des datasets
            merged_data = transformer.merge_datasets(clean_election_data, clean_socioeconomic_data)
            
            # Préparation pour la modélisation
            final_data = transformer.prepare_for_modeling(merged_data)
            
            # Sauvegarde des données transformées
            final_data.to_csv('data/processed/final_dataset.csv', index=False)
            print("Données transformées et sauvegardées avec succès.")
            
        except Exception as e:
            print(f"Erreur lors du processus ETL: {str(e)}")
        
        print("Processus ETL terminé.")

if __name__ == "__main__":
    main()