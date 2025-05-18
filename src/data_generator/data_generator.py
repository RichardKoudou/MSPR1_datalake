import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_commune_data(num_communes=10, years=range(2017, 2024)):
    # Générer des données de base pour les communes
    communes = {
        'commune_id': range(1, num_communes + 1),
        'nom_commune': [f'Commune_{i}' for i in range(1, num_communes + 1)],
        'population': np.random.randint(5000, 100000, num_communes),
        'departement': np.random.randint(1, 96, num_communes)
    }
    
    return pd.DataFrame(communes)

def generate_socio_economic_data(communes_df, years):
    # Générer des données socio-économiques pour chaque commune et année
    data = []
    
    for year in years:
        for _, commune in communes_df.iterrows():
            data.append({
                'commune_id': commune['commune_id'],
                'annee': year,
                'taux_chomage': round(np.random.uniform(5, 15), 2),
                'revenu_median': round(np.random.uniform(20000, 45000), 2),
                'taux_criminalite': round(np.random.uniform(20, 100), 2),
                'niveau_education': round(np.random.uniform(60, 95), 2),
                'densite_population': round(commune['population'] / np.random.uniform(10, 50), 2)
            })
    
    return pd.DataFrame(data)

def generate_election_results(communes_df, years):
    # Générer des résultats électoraux
    partis = ['Parti_A', 'Parti_B', 'Parti_C', 'Parti_D']
    data = []
    
    for year in years:
        for _, commune in communes_df.iterrows():
            # Générer des pourcentages qui somment à 100
            votes = np.random.dirichlet(np.ones(len(partis))) * 100
            participation = round(np.random.uniform(60, 85), 2)
            
            for parti, vote_percentage in zip(partis, votes):
                data.append({
                    'commune_id': commune['commune_id'],
                    'annee': year,
                    'parti': parti,
                    'pourcentage_votes': round(vote_percentage, 2),
                    'taux_participation': participation
                })
    
    return pd.DataFrame(data)

def main():
    # Paramètres de génération
    years = range(2017, 2024)
    num_communes = 50
    
    print(f"Génération des données pour {num_communes} communes de {min(years)} à {max(years)}...")
    
    # Générer les données
    communes_df = generate_commune_data(num_communes, years)
    print(f"✓ Données des communes générées ({len(communes_df)} communes)")
    
    socio_economic_df = generate_socio_economic_data(communes_df, years)
    print(f"✓ Données socio-économiques générées ({len(socio_economic_df)} enregistrements)")
    
    election_df = generate_election_results(communes_df, years)
    print(f"✓ Résultats électoraux générés ({len(election_df)} enregistrements)")
    
    # Validation des données
    assert all(communes_df['population'] >= 0), "Erreur: populations négatives détectées"
    assert all(socio_economic_df['taux_chomage'].between(0, 100)), "Erreur: taux de chômage invalides"
    assert all(election_df['pourcentage_votes'].between(0, 100)), "Erreur: pourcentages de votes invalides"
    
    print("\nSauvegarde des données...")
    # Sauvegarder les données en CSV
    communes_df.to_csv('data/fake/communes.csv', index=False)
    socio_economic_df.to_csv('data/fake/socio_economic.csv', index=False)
    election_df.to_csv('data/fake/election_results.csv', index=False)
    print("✓ Données sauvegardées avec succès dans le dossier 'data/fake/'")


if __name__ == '__main__':
    main()