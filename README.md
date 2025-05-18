# Projet de Prédiction Électorale – POC

> Travail réalisé dans le cadre de la MSPR « Data Lake & IA ». Pour le cahier des charges détaillé, consultez le [sujet](Subject.md).

---

## ✨ Objectif

Mettre en place une **preuve de concept** pour **Elexxion**, jeune pousse spécialisée dans le conseil électoral, capable de :

1. Collecter puis normaliser des données publiques (INSEE, data.gouv, etc.) ou **générer des données factices** pour accélérer les tests.
2. Croiser ces données avec les résultats électoraux historiques.
3. Entraîner un modèle supervisé afin de **prédire le bloc vainqueur** à +1, +2 et +3 ans.
4. Visualiser indicateurs, corrélations et projections futures.

---

## 🗂️ Arborescence du dépôt

```text
.
├── assets/                # diagrammes, jeu de communes, géojson…
│   ├── architecture.png
│   ├── architecture2.png
│   └── communes.csv
├── init-scripts/          # scripts SQL pour provisionner PostgreSQL
├── src/
│   ├── ingestion/         # loaders + orchestration (mode API ou Fake)
│   ├── transformation/    # transformers & fusion
│   ├── prediction/        # entraînement + prédicteur
│   └── visualization/     # graphiques et cartes
├── notebooks/             # analyses exploratoires
├── test/                  # tests unitaires (pytest)
├── config.yml             # active le mode `api` ou `fake`
├── main.py                # CLI d’orchestration (ingest → train → predict…)
├── docker-compose.yml     # services : PostgreSQL, MinIO, Kafka…
└── requirements.txt       # dépendances Python
```

> **Nouveauté** : la CLI expose le switch `--mode fake|api` pour alterner entre données factices et réelles.

---

## 🔄 Pipeline de traitement

1. Avec Dataiku DSS,

![Architecture du Projet](assets/architecture.png)
  
2. Avec des scripts Python  

```mermaid
graph LR
    subgraph 1[Ingestion]
        A1["« Loaders » '(elections, socio_eco…)'"] -->|Parquet| A2[data/raw]
    end

    subgraph 2[Transformation]
        A2 --> B1[Transformers]
        B1 -->|Parquet| B2[data/curated]
    end

    subgraph 3[Modélisation]
        B2 --> C1[Training Pipeline]
        C1 -->|joblib| C2[models/]
        C2 --> C3[Predictor]
    end

    subgraph 4[Visualisation]
        B2 --> D1[Heatmaps/Maps]
        C3 --> D2[Projections +1/+2/+3]
    end
```

---

## ⚙️ Lancer le projet

### 1. Prérequis

* Docker ≥ 24 (pour la stack optionnelle Kafka / MinIO / PostgreSQL)
* Python 3.11 (ou créez un venv)

### 2. Installation rapide

```bash
# clonage
$ git clone <url-du-repo>
$ cd mspr1_elexxion

# dépendances
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# services – optionnels
$ docker-compose up -d   # détachable
```

### 3. Exécution du pipeline

Mode **données factices** (le plus rapide pour tester l’enchaînement complet) :

```bash
$ python main.py --step all --mode fake
```

Vous devriez obtenir :

```
✅ elections – 5 000 lignes
✅ socio_eco – 36 000 lignes
✅ communes  – 12 000 lignes
✅ Transformation terminée : (36 000, …)
Accuracy : 0.81
```

Mode **API** (pousse les loaders vers les sources réelles déclarées dans `config.yml`) :

```bash
$ python3 main.py --step ingest --mode api  # puis --step transform, train…
```

### 4. Tests unitaires

```bash
$ pytest -q   # ingestion, transformation, prédiction
```

---

## 🛠️ Pile technologique

| Couche              | Outils principaux                       |
| ------------------- | --------------------------------------- |
| ETL                 | Python 3.11 · Pandas · Faker · Requests |
| Stockage            | Parquet (Datalake MinIO) · PostgreSQL   |
| Modélisation        | Scikit‑learn (RandomForest)             |
| Viz                 | Matplotlib · Geopandas                  |
| Orchestration       | Docker · docker‑compose                 |
| Streaming optionnel | Apache Kafka                            |

---

## 🤝 Contribution
=======
# Projet de Prédiction Électorale - POC

> Ce projet est réalisé dans le cadre d'une MSPR. Pour plus de détails sur les objectifs et les exigences du projet, consultez le [sujet détaillé](Subject.md).

## 📋 Description du Projet

Preuve de concept (POC) développée pour Elexxion, une start-up spécialisée dans le conseil électoral. L'objectif est de créer un modèle d'intelligence artificielle capable de prédire les tendances électorales en se basant sur des données socio-économiques, de sécurité et d'emploi.

## 🏗️ Structure du Projet

```shell
.
├── notebooks/           # Notebooks Jupyter pour l'analyse exploratoire
├── src/                 # Code source du projet
│   ├── etl/             # Scripts de collecte et transformation des données
│   ├── models/          # Modèles de prédiction
│   └── visualization/   # Outils de visualisation
├── init-scripts/        # Scripts d'initialisation de la base de données
└── docker-compose.yml   # Configuration Docker
```

## 📊 Architecture du Projet

- ![Architecture du Projet](assets/architecture.png)
  
```mermaid
graph TB
    subgraph Infrastructure["🏗️ Infrastructure"]
        D[("Docker 🐳")]
        KFK["Apache Kafka"]
        MINIO["MinIO Datalake"]
        PSQL["PostgreSQL"]
    end

    subgraph DataProcessing["📊 Traitement des Données"]
        SCRP["Web Scraping 🕷️"]
        ETL["ETL Scripts 🔄"]
        DSS["Dataiku DSS"]
        NB["Notebooks Jupyter 📓"]
    end

    subgraph PythonStack["🐍 Stack Python"]
        PY["Python 3.x"]
        PY --> PD["Pandas & NumPy"]
        PY --> SKL["Scikit-learn"]
        PY --> MPL["Matplotlib"]
    end

    subgraph ProjectModules["📦 Modules du Projet"]
        direction TB
        SRC["src/"]
        SRC --> ETLM["etl/"]
        SRC --> MOD["models/"]
        SRC --> VIS["visualization/"]
    end

    %% Flux de données
    SCRP --> KFK
    KFK --> ETL
    ETL --> MINIO
    MINIO --> DSS
    DSS --> PSQL
    NB --> PSQL
    ETLM --> PY
    MOD --> SKL
    VIS --> MPL

    style Infrastructure fill:#e1f5fe,stroke:#01579b
    style DataProcessing fill:#f3e5f5,stroke:#4a148c
    style PythonStack fill:#e8f5e9,stroke:#1b5e20
    style ProjectModules fill:#fff3e0,stroke:#e65100
```

## 🛠️ Technologies Utilisées

- **Python 3.x** avec les bibliothèques :
  - Pandas & NumPy : Manipulation des données
  - Scikit-learn : Modélisation prédictive
  - Matplotlib : Visualisation
- **Infrastructure Data :**
  - Apache Kafka : Streaming de données en temps réel
  - MinIO : Stockage d'objets S3-compatible
  - PostgreSQL : Base de données relationnelle
- **Outils de Data Science :**
  - Dataiku DSS : Plateforme de Data Science
  - Kafka UI : Interface de gestion Kafka
- **Docker** : Conteneurisation et orchestration des services
- **SQL** : Requêtage et analyse des données

## 🚀 Installation et Démarrage

1. **Cloner le repository** :

   ```bash
   git clone <url-du-repo>
   cd <nom-du-repo>
   ```

2. **Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer les conteneurs Docker** :

   ```bash
   docker-compose up -d
   ```

4. **Exécuter le projet** :

   ```bash
   python main.py
   ```

## 📊 Utilisation  

Le projet se compose de trois parties principales :

1. **Collecte et Transformation des Données** :
   - Scripts Python dans `src/etl/` pour collecter et transformer les données.
   - Utilisation de Docker pour la gestion des bases de données.
2. **Modélisation Prédictive** :
   - Scripts Python dans `src/models/` pour la création et l'entraînement des modèles.
3. **Visualisation des Résultats** :
   - Scripts Python dans `src/visualization/` pour générer des visualisations.
  
## 🤝 Contribution  

Ce projet est développé dans le cadre d'un travail d'équipe de 4-5 étudiants. Pour contribuer :

1. Forkez le repository.
2. Créez une nouvelle branche : `git checkout -b feature/nom-de-la-fonctionnalité`.
3. Faites vos modifications et commit : `git commit -m 'Ajout de la fonctionnalité X'`.
4. Poussez vers la branche : `git push origin feature/nom-de-la-fonctionnalité`.
5. Ouvrez une Pull Request.


---

## Licence

Ce dépôt est fourni dans le cadre d’un exercice académique ; la licence par défaut est **MIT**.

