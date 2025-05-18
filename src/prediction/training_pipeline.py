import pathlib, joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATA      = pathlib.Path("data/curated/dataset.parquet")
MODEL_DIR = pathlib.Path("models"); MODEL_DIR.mkdir(exist_ok=True)
MODEL_F   = MODEL_DIR / "electoral_model.joblib"
METRIC_F  = MODEL_DIR / "metrics.txt"

def train():
    df = pd.read_parquet(DATA)

    y = df["gagnant_flag"]
    X = df.drop(columns=["gagnant_flag", "gagnant"])

    num = X.select_dtypes("number").columns
    cat = X.select_dtypes("object").columns

    pipe = Pipeline([
        ("prep",
         ColumnTransformer([
            ("num", StandardScaler(), num),
            ("cat", OneHotEncoder(handle_unknown='ignore'), cat)
         ])),
        ("clf", RandomForestClassifier(
            n_estimators=500, max_depth=None, random_state=42))
    ])

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)

    pipe.fit(X_tr, y_tr)
    preds = pipe.predict(X_te)

    acc = accuracy_score(y_te, preds)
    rep = classification_report(y_te, preds, digits=3)

    MODEL_F.unlink(missing_ok=True)
    joblib.dump(pipe, MODEL_F)

    METRIC_F.write_text(
        f"Accuracy : {acc:.3f}\n\n---\n{rep}\n"
    )
    print(f"✅  Modèle enregistré → {MODEL_F}")
    print(f"ℹ️  Accuracy : {acc:.3f} (détails dans {METRIC_F})")

if __name__ == "__main__":
    train()