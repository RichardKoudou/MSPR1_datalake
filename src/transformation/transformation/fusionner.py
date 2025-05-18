import pandas as pd

class Fusionner:
    def transform(self, elections: pd.DataFrame,
                  socio: pd.DataFrame) -> pd.DataFrame:
        merged = elections.merge(
            socio, on=["code_commune", "annee"], how="inner", validate="1:1"
        )
        # variable cible binaire : 1 si gagnant ∈ ['Bloc A', 'Candidat A', …]
        merged["gagnant_flag"] = merged["gagnant"].isin(
            ["Macron", "Bloc A", "Candidat A"]
        ).astype(int)
        return merged
