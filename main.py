

def main():
    """
    Main function to execute the data collection, transformation, prediction, and visualization.
    """
    from src.etl.data_collector import DataCollector

    # Initialisation du collecteur de données
    collector = DataCollector()

    # Liste des URLs pour la collecte de données
    urls = [
        "https://www.data.gouv.fr/fr/pages/donnees-emploi/",
        "https://www.data.gouv.fr/fr/pages/donnees-elections/",
        "https://www.data.gouv.fr/fr/pages/donnees-securite/"
    ]

    # Lancement de la collecte de données
    print("Démarrage de la collecte des données...")
    collector.collect_all_data(urls)
    print("Collecte des données terminée.")


if __name__ == "__main__":
    main()