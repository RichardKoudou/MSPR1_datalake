from .base_loader import BaseLoader
from .loader_utils import load_communes_csv
import pandas as pd

class CommunesLoader(BaseLoader):
    """Toujours local (CSV ou Parquet). Pas de mode fake/api ici."""
    def load(self) -> pd.DataFrame:
        return load_communes_csv(self.cfg.get("file"))
