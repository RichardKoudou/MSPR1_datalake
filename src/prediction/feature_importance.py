# src/prediction/feature_importance.py
import joblib, pandas as pd
import matplotlib.pyplot as plt, pathlib

MODEL = "models/electoral_model.joblib"
model = joblib.load(MODEL)["clf"]              # accéder au RandomForest

imp = pd.Series(model.feature_importances_)
imp.nlargest(15).plot(kind="barh")
plt.title("Top-15 importances (RandomForest)")
plt.tight_layout(); plt.show()
