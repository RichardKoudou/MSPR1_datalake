import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

class ElectionPredictor:
    """Classe pour la prédiction des tendances électorales"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.accuracy = None
        self.feature_importance = None

    def prepare_data(self, df, target_column, test_size=0.2):
        """Prépare les données pour l'entraînement"""
        # Séparation des features et de la cible
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Division en sets d'entraînement et de test
        return train_test_split(X, y, test_size=test_size, random_state=42)

    def train(self, X_train, y_train):
        """Entraîne le modèle prédictif"""
        self.model.fit(X_train, y_train)
        self.feature_importance = pd.Series(
            self.model.feature_importances_,
            index=X_train.columns
        ).sort_values(ascending=False)

    def evaluate(self, X_test, y_test):
        """Évalue la précision du modèle"""
        predictions = self.model.predict(X_test)
        self.accuracy = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        return {
            'r2_score': self.accuracy,
            'mse': mse,
            'rmse': np.sqrt(mse)
        }

    def predict_future(self, X_future, periods=3):
        """Génère des prédictions pour les années futures"""
        predictions = []
        current_data = X_future.copy()

        for i in range(periods):
            pred = self.model.predict(current_data)
            predictions.append(pred)
            # TODO: Mettre à jour les données pour la prédiction suivante
            # Implémenter la logique de mise à jour des features

        return predictions

    def get_most_important_features(self, n=5):
        """Retourne les features les plus importantes"""
        return self.feature_importance.head(n)