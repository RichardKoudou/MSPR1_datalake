import pandas as pd

class SocioEcoTransformer:
    """
    - Nettoie les indicateurs
    - Impute (median) pour les valeurs manquantes
    """
    def transform(self, socio: pd.DataFrame) -> pd.DataFrame:
        socio = socio.copy()
        # types
        socio["annee"] = socio["annee"].astype(int)
        num_cols = socio.select_dtypes("number").columns
        socio[num_cols] = socio[num_cols].fillna(socio[num_cols].median())
        return socio
