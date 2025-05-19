import pandas as pd, matplotlib.pyplot as plt, pathlib, seaborn as sns
sns.set_theme()                 # style simple

#CURATED = pathlib.Path("data/curated/dataset.parquet")
CURATED = pathlib.Path("data-test/train.parquet")

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