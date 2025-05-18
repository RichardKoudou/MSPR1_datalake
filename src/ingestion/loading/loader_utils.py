import pathlib, pandas as pd, yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]      # repo root (parent de src)

def read_config(cfg_path: str | pathlib.Path = "config.yml") -> dict:
    return yaml.safe_load(pathlib.Path(cfg_path).read_text())

def load_communes_csv(path: str | pathlib.Path | None = None) -> pd.DataFrame:
    path = ROOT / (path or "assets/communes.csv")
    df = pd.read_csv(path)
    # uniformise les colonnes
    df.rename(columns=lambda c: c.strip().lower(), inplace=True)
    # Renommer les colonnes pour correspondre aux noms attendus
    column_mapping = {
        "insee_code": "code_commune",
        "name": "nom_commune",
        "department": "code_dept"
    }
    df = df.rename(columns=column_mapping)
    return df[["code_commune", "nom_commune", "code_dept"]]
