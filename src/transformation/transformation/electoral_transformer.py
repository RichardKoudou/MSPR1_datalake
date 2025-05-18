import pandas as pd

class ElectoralTransformer:
    """
    - Agrège les voix par commune/année/candidat
    - Détermine le gagnant (voix max)
    """
    def transform(self, elections: pd.DataFrame,
                  communes: pd.DataFrame) -> pd.DataFrame:
        agg = (elections
               .groupby(["annee", "code_commune", "candidat"], as_index=False)
               ["voix"].sum())
        agg["rank"] = agg.groupby(["annee", "code_commune"])["voix"]\
                         .rank(ascending=False, method="first")
        winners = (agg[agg["rank"] == 1]
                   .drop(columns="rank")
                   .rename(columns={"candidat": "gagnant"}))
        # merge pour récupérer nom_commune
        return winners.merge(communes, on="code_commune", how="left")
