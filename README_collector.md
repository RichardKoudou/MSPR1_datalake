# Documentation du Collecteur de Données

## Améliorations apportées

Le script `collector.py` a été amélioré pour mieux répondre aux besoins du projet de prédiction électorale. Voici les principales améliorations :

### 1. Organisation des données par catégorie

Les données sont désormais organisées dans des sous-répertoires selon leur catégorie :
- `election` : Données électorales (résultats, participation, etc.)
- `socioeco` : Données socio-économiques (emploi, revenus, etc.)
- `security` : Données de sécurité (criminalité, etc.)
- `other` : Autres données non catégorisées

### 2. Filtrage intelligent des données

Le script utilise des listes de mots-clés pour catégoriser automatiquement les fichiers téléchargés :
- Mots-clés électoraux : élection, vote, scrutin, etc.
- Mots-clés socio-économiques : emploi, chômage, revenu, etc.
- Mots-clés sécurité : sécurité, crime, délinquance, etc.

### 3. Gestion robuste des erreurs

- Tentatives multiples de téléchargement en cas d'échec
- Gestion des timeouts et des erreurs de connexion
- Messages d'erreur explicites

### 4. Support optionnel pour MinIO

Possibilité de stocker les données dans MinIO (stockage objet compatible S3) en plus du stockage local.

### 5. Configuration via variables d'environnement

Utilisation d'un fichier `.env` pour configurer :
- L'URL de base
- Les paramètres de connexion MinIO
- D'autres paramètres configurables

## Utilisation

### Installation des dépendances

```bash
pip install requests beautifulsoup4 python-dotenv boto3
```

### Configuration

Modifiez le fichier `.env` selon vos besoins :

```
# Configuration de base
BASE_URL=https://www.data.gouv.fr

# Configuration MinIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=mspr-data
```

### Exécution

```bash
python src/etl/collector.py
```

### Activation de MinIO

Pour activer le stockage dans MinIO, modifiez la ligne suivante dans la fonction `main()` :

```python
collector = DataCollector(use_minio=True)
```

## Structure du code

Le script utilise une approche orientée objet avec la classe `DataCollector` qui encapsule toutes les fonctionnalités :

- `__init__` : Initialisation et configuration
- `setup_minio` : Configuration de la connexion MinIO
- `is_data_link` : Détection des liens de données
- `determine_category` : Catégorisation des fichiers
- `find_data_links` : Recherche des liens de données sur une page
- `download_file` : Téléchargement et stockage d'un fichier
- `collect_data` : Orchestration du processus de collecte