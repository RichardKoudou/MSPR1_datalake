import joblib, pathlib, pandas as pd, datetime as dt

MODEL_F = pathlib.Path("models/electoral_model.joblib")
CURATED = pathlib.Path("data-test/train.parquet")
OUT_DIR = pathlib.Path("data/predictions"); OUT_DIR.mkdir(exist_ok=True)

def predict(input_path: str | pathlib.Path | None = None,
            out_file: str | None = None) -> pathlib.Path:
    model = joblib.load(MODEL_F)
    df    = pd.read_parquet(input_path or CURATED)

    X = df.drop(columns=["gagnant_flag", "gagnant"], errors="ignore")
    proba_A = model.predict_proba(X)[:, 1]

    res = df[["code_commune", "annee"]].copy()
    res["proba_bloc_A"] = proba_A

    out_path = pathlib.Path(
        out_file or OUT_DIR / f"pred_{dt.date.today()}.csv"
    )
    res.to_csv(out_path, index=False)
    print(f" Prédictions sauvegardées → {out_path}")
    return out_path
