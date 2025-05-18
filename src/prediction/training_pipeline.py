import pandas as pd, joblib, pathlib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline  import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble    import RandomForestClassifier
from sklearn.metrics     import accuracy_score
from sklearn.model_selection import train_test_split

DATA = pathlib.Path("data/curated/dataset.parquet")

def train():
    df = pd.read_parquet(DATA)

    y   = df["gagnant"]          # 1 = bloc A, 0 = bloc B, à adapter
    X   = df.drop(columns=["gagnant"])

    num = X.select_dtypes("number").columns
    cat = X.select_dtypes("object").columns

    preproc = ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat)
    ])

    clf = RandomForestClassifier(n_estimators=500, random_state=42)

    pipe = Pipeline([("prep", preproc), ("model", clf)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)

    pipe.fit(X_train, y_train)
    acc = accuracy_score(y_test, pipe.predict(X_test))
    print(f"Accuracy : {acc:.3f}")

    joblib.dump(pipe, "models/electoral_model.joblib")

if __name__ == "__main__":
    train()
