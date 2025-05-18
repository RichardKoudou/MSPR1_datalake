from .base_loader import BaseLoader
from .loader_utils import load_communes_csv
import pandas as pd, numpy as np, requests, io, faker, random, datetime as dt

YEARS = [2012, 2017, 2022]

# ---------- API ----------
class SocioEcoAPILoader(BaseLoader):
    def load(self) -> pd.DataFrame:
        # Exemple : l’API INSEE "Bilan démographique"
        resp = requests.get(self.cfg["url"], timeout=60)
        df = pd.read_csv(io.StringIO(resp.text), sep=";")
        return df.rename(columns=str.lower)

# ---------- FAKE ----------
class SocioEcoFakeLoader(BaseLoader):
    def load(self) -> pd.DataFrame:
        fake = faker.Faker("fr_FR")
        communes = load_communes_csv()["code_commune"].tolist()
        rows = []
        rng  = np.random.default_rng(seed=self.cfg.get("seed", 42))

        for code in communes:
            for year in YEARS:
                rows.append({
                    "code_commune": code,
                    "annee": year,
                    "population": rng.integers(500, 200_000),
                    "tx_chomage": rng.uniform(4, 18),          # %
                    "revenu_median": rng.integers(15_000, 40_000),
                    "tx_criminalite": rng.uniform(1, 15),      # pour 1 000 hab.
                })
        return pd.DataFrame(rows)
