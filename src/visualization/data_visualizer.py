# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd
# import numpy as np

# class DataVisualizer:
#     """Classe pour la création de visualisations des données et prédictions"""

#     def __init__(self):
#         plt.style.use('seaborn')
#         self.colors = sns.color_palette('husl')

#     def plot_correlation_matrix(self, df, title='Matrice de Corrélation'):
#         """Affiche une matrice de corrélation des variables"""
#         plt.figure(figsize=(12, 8))
#         correlation_matrix = df.corr()
#         sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
#         plt.title(title)
#         plt.tight_layout()
#         return plt.gcf()

#     def plot_feature_importance(self, importance_df, title='Importance des Variables'):
#         """Visualise l'importance des features dans le modèle"""
#         plt.figure(figsize=(10, 6))
#         sns.barplot(x=importance_df.values, y=importance_df.index)
#         plt.title(title)
#         plt.xlabel('Importance')
#         plt.tight_layout()
#         return plt.gcf()

#     def plot_predictions(self, actual, predicted, title='Prédictions vs Réalité'):
#         """Compare les valeurs prédites aux valeurs réelles"""
#         plt.figure(figsize=(10, 6))
#         plt.scatter(actual, predicted, alpha=0.5)
#         plt.plot([actual.min(), actual.max()], [actual.min(), actual.max()], 'r--', lw=2)
#         plt.xlabel('Valeurs Réelles')
#         plt.ylabel('Prédictions')
#         plt.title(title)
#         plt.tight_layout()
#         return plt.gcf()

#     def plot_future_predictions(self, predictions, dates, confidence_intervals=None):
#         """Visualise les prédictions futures avec intervalles de confiance optionnels"""
#         plt.figure(figsize=(12, 6))
#         plt.plot(dates, predictions, 'b-', label='Prédictions')

#         if confidence_intervals is not None:
#             lower, upper = confidence_intervals
#             plt.fill_between(dates, lower, upper, color='b', alpha=0.1, label='Intervalle de Confiance')

#         plt.title('Prédictions Futures')
#         plt.xlabel('Date')
#         plt.ylabel('Valeur Prédite')
#         plt.legend()
#         plt.grid(True)
#         plt.tight_layout()
#         return plt.gcf()

#     def plot_trend_analysis(self, df, time_column, value_column, title='Analyse des Tendances'):
#         """Analyse et visualise les tendances temporelles"""
#         plt.figure(figsize=(12, 6))
#         sns.regplot(data=df, x=time_column, y=value_column, scatter_kws={'alpha':0.5})
#         plt.title(title)
#         plt.xlabel('Temps')
#         plt.ylabel('Valeur')
#         plt.tight_layout()
#         return plt.gcf()

#     def save_plot(self, fig, filename):
#         """Sauvegarde une figure dans un fichier"""
#         fig.savefig(f'reports/figures/{filename}.png', dpi=300, bbox_inches='tight')
#         plt.close(fig)

import pandas as pd, matplotlib.pyplot as plt, pathlib, seaborn as sns
sns.set_theme()                 # style simple

#CURATED = pathlib.Path("data/curated/dataset.parquet")
CURATED = pathlib.Path("../../data/curated/dataset.parquet")

def correlation_matrix():
    df = pd.read_parquet(CURATED)
    num = df.select_dtypes("number")
    corr = num.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=False, cmap="coolwarm")
    plt.title("Corrélations – variables numériques")
    plt.tight_layout()
    plt.show()

def vote_map(year: int):
    df  = pd.read_parquet(CURATED).query("annee == @year")
    geo = pd.read_file("assets/communes.geojson")  # shapefile ou geojson
    merged = geo.merge(df, on="code_commune")
    merged.plot(column="gagnant", figsize=(12, 10), legend=True)
    plt.title(f"Résultats – {year}")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    correlation_matrix()
    vote_map(2022)