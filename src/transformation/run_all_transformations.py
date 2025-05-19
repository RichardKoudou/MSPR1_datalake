import boto3
import pandas as pd
from io import BytesIO
from sklearn.model_selection import train_test_split
import yaml
import os

# Chemin absolu vers config.yml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.yml")

# Chargement du config.yml
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

aws_config = config["aws"]

# Création du client boto3 avec les identifiants explicites
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_config["access_key"],
    aws_secret_access_key=aws_config["secret_access_key"],
    region_name=aws_config.get("region", "eu-north-1")
)

BUCKET_NAME = aws_config["bucket"]
IDF_DEPARTMENTS = {"75", "77", "78", "91", "92", "93", "94", "95"}

def list_s3_files(prefix):
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [obj["Key"] for obj in response["Contents"] if not obj["Key"].endswith("/")]

def read_files_from_s3(prefix):
    files = list_s3_files(prefix)
    dataframes = []

    for file in files:
        print(f" Lecture de {file} ...")
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=file)
        content = obj["Body"].read()

        df = None
        errors = []

        # 1. Essayer CSV utf-8
        try:
            df = pd.read_csv(BytesIO(content), sep=";", encoding="utf-8")
            print(f" Fichier CSV chargé (utf-8) : {file}")
        except Exception as e:
            errors.append(f"csv utf-8: {e}")

        # 2. Essayer CSV latin1
        if df is None:
            try:
                df = pd.read_csv(BytesIO(content), sep=";", encoding="latin1")
                print(f" Fichier CSV chargé (latin1) : {file}")
            except Exception as e:
                errors.append(f"csv latin1: {e}")

        # 3. Essayer Excel avec différents engines
        if df is None:
            for engine in ['openpyxl', 'xlrd', 'pyxlsb']:
                try:
                    df = pd.read_excel(BytesIO(content), engine=engine)
                    print(f" Fichier Excel chargé avec engine={engine} : {file}")
                    break
                except Exception as e:
                    errors.append(f"excel engine={engine}: {e}")

        # 4. Essayer JSON
        if df is None:
            try:
                import json
                raw_json = content.decode('utf-8')
                data = json.loads(raw_json)
                df = pd.json_normalize(data)
                print(f" Fichier JSON chargé : {file}")
            except Exception as e:
                errors.append(f"json: {e}")

        # 5. Essayer lecture brute en texte avec erreurs ignorées (fallback ultime)
        if df is None:
            try:
                raw_text = content.decode('utf-8', errors='replace')
                from io import StringIO
                df = pd.read_csv(StringIO(raw_text), sep=";", engine='python')
                print(f" Fichier lu en texte avec erreurs ignorées : {file}")
            except Exception as e:
                errors.append(f"lecture texte fallback: {e}")

        if df is not None:
            dataframes.append(df)
        else:
            print(f" Impossible de lire {file}, erreurs: {errors}")

    if not dataframes:
        raise ValueError(f"Aucun fichier valide trouvé dans {prefix}")

    return pd.concat(dataframes, ignore_index=True)

def clean_and_merge(elections, communes, socio_eco):
    # Nettoyage noms colonnes
    elections.columns = elections.columns.str.lower().str.strip()
    socio_eco.columns = socio_eco.columns.str.lower().str.strip()

    if communes is not None:
        communes.columns = communes.columns.str.lower().str.strip()

    # Vérification et merge selon présence colonnes code_commune
    code_commune_elections = 'code_commune' in elections.columns
    code_commune_communes = communes is not None and 'code_commune' in communes.columns
    code_commune_socio = 'code_commune' in socio_eco.columns

    df = elections.copy()

    if code_commune_communes:
        communes["code_departement"] = communes["code_commune"].astype(str).str[:2]
        idf_communes = communes[communes["code_departement"].isin(IDF_DEPARTMENTS)]
        if code_commune_elections:
            df = df.merge(idf_communes, on="code_commune", how="inner")
        else:
            # Pas de code_commune dans elections, impossible merge
            print("Warning: 'code_commune' absent dans elections, commune ignorée.")
    else:
        print("Info: dataset communes ignoré.")

    if code_commune_socio:
        if 'code_commune' in df.columns:
            df = df.merge(socio_eco, on="code_commune", how="left")
        else:
            # Pas de code_commune dans df pour merge, concat socio_eco ? 
            print("Warning: 'code_commune' absent dans données fusionnées, socio_eco non fusionné.")
    else:
        print("Info: dataset socio_eco sans 'code_commune', fusion impossible.")

    # Calculs optionnels
    if "nombre_votants" in df.columns and "nombre_inscrits" in df.columns:
        df["taux_participation"] = df["nombre_votants"] / df["nombre_inscrits"]

    if "voix" in df.columns and "nombre_votants" in df.columns:
        df["resultat_candidat"] = df["voix"] / df["nombre_votants"]

    return df

def clean_df_for_parquet(df):
    # Supprimer colonnes vides
    df = df.dropna(axis=1, how='all')
    # Supprimer colonnes 'unnamed'
    df = df.loc[:, ~df.columns.str.lower().str.startswith('unnamed')]
    return df

def fix_object_columns(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)
    return df

def select_relevant_columns(df):
    # Liste indicative, à ajuster selon ta compréhension des données
    relevant_cols = [
        "Code du département",
        "Libellé du département",
        "Code de la circonscription",
        "Libellé de la circonscription",
        "Libellé de la commune",
        "Code du b.vote",
        "Inscrits",
        "Abstentions",
        "Votants",
        "Blancs",
        "Nuls",
        "Exprimés",
        "Sexe",
        "Nom",
        "Prénom",
        "Voix",
        "Code de la commune"
        "resultat_candidat",
        "nombre_votants",
        "nombre_inscrits",
        "voix",
        "population",
        "revenu_median",
        "chomage",
        "age_median",
        "taille_menage"
    ]
    # Retourner seulement colonnes existantes parmi les choisies
    cols = [c for c in relevant_cols if c in df.columns]
    print(f"Colonnes sélectionnées pour export: {cols}")
    return df[cols]

def main():
    print("Connexion à S3 initialisée avec succès.")
    print("Lecture des fichiers S3...")
    elections = read_files_from_s3("raw/elections/")
    try:
        communes = read_files_from_s3("raw/communes/")
    except Exception as e:
        print(f"Impossible de lire raw/communes/: {e}")
        communes = None
    socio_eco = read_files_from_s3("raw/socio_eco/")

    print("Fusion et nettoyage...")
    merged_df = clean_and_merge(elections, communes, socio_eco)

    print(f"Dataset final avant nettoyage: {merged_df.shape[0]} lignes, {merged_df.shape[1]} colonnes")

    merged_df = clean_df_for_parquet(merged_df)
    merged_df = fix_object_columns(merged_df)
    merged_df = select_relevant_columns(merged_df)

    print(f"Dataset final après sélection: {merged_df.shape[0]} lignes, {merged_df.shape[1]} colonnes")

    print("Split train/test...")
    train_df, test_df = train_test_split(merged_df, test_size=0.2, random_state=42)

    os.makedirs("data-test", exist_ok=True)
    train_df.to_parquet("data-test/train.parquet", index=False)
    test_df.to_parquet("data-test/test.parquet", index=False)
    print("Fichiers exportés localement")

    print("Upload des fichiers vers S3...")
    s3.upload_file("data-test/train.parquet", BUCKET_NAME, "processed/train.parquet")
    print("train.parquet envoyé dans S3.")
    s3.upload_file("data-test/test.parquet", BUCKET_NAME, "processed/test.parquet")
    print("Fichiers uploadés dans S3 → dossier 'processed/'")
    
    print("Upload des fichiers vers S3...")
    try:
        s3.upload_file("data-test/train.parquet", BUCKET_NAME, "processed/train.parquet")
        print(f"train.parquet envoyé dans S3 à s3://{BUCKET_NAME}/processed/train.parquet")
    except Exception as e:
        print(f"Erreur upload train.parquet : {e}")

    try:
        s3.upload_file("data-test/test.parquet", BUCKET_NAME, "processed/test.parquet")
        print(f"test.parquet envoyé dans S3 à s3://{BUCKET_NAME}/processed/test.parquet")
    except Exception as e:
        print(f"Erreur upload test.parquet : {e}")

    # Lister les fichiers dans le dossier processed/
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="processed/")
    if "Contents" in response:
        print("Fichiers présents dans processed/ :")
        for obj in response["Contents"]:
            print(" -", obj["Key"])
    else:
        print("Aucun fichier trouvé dans processed/")


if __name__ == "__main__":
    main()
