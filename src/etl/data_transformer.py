import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataTransformer:
    """Classe pour la transformation et le nettoyage des données collectées"""

    def __init__(self):
        self.scaler = StandardScaler()

    def clean_election_data(self, df):
        """Nettoie et transforme les données électorales"""
        # Supprimer les doublons
        df = df.drop_duplicates()
        
        # Gérer les valeurs manquantes
        df['votes'] = df['votes'].fillna(0)
        df['participation'] = df['participation'].fillna(df['participation'].mean())
        
        # Normaliser les formats de date
        df['date'] = pd.to_datetime(df['date'])
        
        # Standardiser les noms de colonnes
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        return df

    def clean_socioeconomic_data(self, df):
        """Nettoie et transforme les données socio-économiques"""
        # Standardiser les valeurs numériques
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        df[numeric_columns] = self.scaler.fit_transform(df[numeric_columns])
        
        # Encoder les variables catégorielles
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = pd.Categorical(df[col]).codes
        
        # Agréger les données par zone géographique
        df = df.groupby('zone_geo').agg({
            'revenu_moyen': 'mean',
            'taux_chomage': 'mean',
            'niveau_education': 'mean',
            'indice_securite': 'mean'
        }).reset_index()
        
        return df

    def merge_datasets(self, election_df, socioeconomic_df):
        """Fusionne les différents jeux de données"""
        # Vérifier la cohérence temporelle
        election_df['annee'] = election_df['date'].dt.year
        
        # Fusion sur la zone géographique et l'année
        merged_df = pd.merge(
            election_df,
            socioeconomic_df,
            on=['zone_geo', 'annee'],
            how='inner'
        )
        
        # Gérer les conflits de données
        merged_df = merged_df.groupby(['zone_geo', 'annee']).agg({
            'votes': 'sum',
            'participation': 'mean',
            'revenu_moyen': 'first',
            'taux_chomage': 'first',
            'niveau_education': 'first',
            'indice_securite': 'first'
        }).reset_index()
        
        return merged_df

    def prepare_for_modeling(self, df):
        """Prépare les données pour la modélisation"""
        # Sélectionner les features pertinentes
        features = ['revenu_moyen', 'taux_chomage', 'niveau_education', 'indice_securite']
        target = 'votes'
        
        X = df[features]
        y = df[target]
        
        # Normaliser les données
        X = self.scaler.fit_transform(X)
        
        # Créer un DataFrame final avec features normalisées et target
        final_df = pd.DataFrame(X, columns=features)
        final_df['target'] = y
        
        return final_df
    
