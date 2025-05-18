# 📈 Guide d’utilisation – Phase *Training*

Ce document explique comment entraîner (ou ré-entraîner) le modèle de prédiction électorale et où retrouver les artefacts produits.  
Il s’appuie sur les scripts fournis dans `src/prediction/`.

---

## 1. Pré-requis

| Élément | Version conseillée |
|---------|-------------------|
| Python  | ≥ 3.9 |
| pip     | ≥ 23 |
| Packages | listés dans `requirements.txt` |

Installez-les :

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Préparation des données

Le modèle attend le *dataset* fusionné **curated** produit par la pipeline ETL.

```bash
# 1) collecte (fake ou api)
python main.py --step ingest --mode fake   # ou --mode api

# 2) transformation + fusion
python main.py --step transform
```

Vérifiez qu’un fichier est présent :

```
data/curated/dataset.parquet
```

---

## 3. Lancer l’entraînement

```bash
python main.py --step train
```

### Que se passe-t-il ?

| Étape | Détails |
|-------|---------|
| **Lecture** | `data/curated/dataset.parquet` |
| **Pré-processing** | - Standardisation des variables numériques  <br>- One-hot encoding des variables catégorielles |
| **Modèle** | `RandomForestClassifier(n_estimators=500, random_state=42)` |
| **Évaluation** | *train / test split* 80 / 20, metrics scikit-learn |
| **Sauvegarde** | - `models/electoral_model.joblib`  *(binaire entraîné)* <br>- `models/metrics.txt`              *(accuracy + classification report)* |

Exemple de sortie :

```
✅  Modèle enregistré → models/electoral_model.joblib
ℹ️  Accuracy : 0.814 (détails dans models/metrics.txt)
```

---

## 4. Lire les métriques

```bash
cat models/metrics.txt
```

```
Accuracy : 0.814

              precision    recall  f1-score   support
...
```

> **Astuce :** ajoutez `src/prediction/feature_importance.py` pour tracer les 15 variables les plus explicatives.

---

## 5. Personnaliser l’entraînement

- **Hyper-paramètres**  
  Modifiez la section `RandomForestClassifier(...)` dans `src/prediction/training_pipeline.py`.
- **Jeu de données différent**  
  Remplacez la constante `DATA` ou passez un chemin alternatif (TODO : ajouter un argument CLI).
- **Reproductibilité**  
  Changez le `random_state` ou le `seed` des loaders pour tester la robustesse.

---

## 6. Dépannage rapide

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| `FileNotFoundError: dataset.parquet` | Étapes ETL non exécutées | Relancer `python main.py --step ingest --mode … && python main.py --step transform` |
| `ImportError: ...` | Dépendance manquante | `pip install -r requirements.txt` |
| Accuracy très basse | — Modèle sous-apprend <br>— Données simulées trop bruitées | - Tester d’autres modèles <br>- Ajuster le paramètre `fake_rows` ou passer en mode *api* |

---

## 7. Étape suivante : prédictions

Une fois le modèle entraîné, générez des scores :

```bash
python main.py --step predict           # sur le jeu complet
# ou
python main.py --step predict --input data/curated/mon_fichier.parquet --output results.csv
```

Consultez ensuite `data/predictions/…csv` ou le fichier de sortie choisi.

---

*Bon entraînement !*