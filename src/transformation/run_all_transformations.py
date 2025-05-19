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

import pandas as pd
from io import BytesIO

import pandas as pd
from io import BytesIO

def read_files_from_s3(prefix):
    files = list_s3_files(prefix)
    dataframes = []

    for file in files:
        print(f"📥 Lecture de {file} ...")
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=file)
        content_type = obj.get('ContentType', '')
        content = obj["Body"].read()

        df = None
        errors = []

        # 1. Essayer CSV utf-8
        try:
            df = pd.read_csv(BytesIO(content), sep=";", encoding="utf-8")
            print(f"✅ Fichier CSV chargé (utf-8) : {file}")
        except Exception as e:
            errors.append(f"csv utf-8: {e}")

        # 2. Essayer CSV latin1
        if df is None:
            try:
                df = pd.read_csv(BytesIO(content), sep=";", encoding="latin1")
                print(f"✅ Fichier CSV chargé (latin1) : {file}")
            except Exception as e:
                errors.append(f"csv latin1: {e}")

        # 3. Essayer Excel avec différents engines
        if df is None:
            for engine in ['openpyxl', 'xlrd', 'pyxlsb']:
                try:
                    df = pd.read_excel(BytesIO(content), engine=engine)
                    print(f"✅ Fichier Excel chargé avec engine={engine} : {file}")
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
                print(f"✅ Fichier JSON chargé : {file}")
            except Exception as e:
                errors.append(f"json: {e}")

        # 5. Essayer lecture brute en texte avec erreurs ignorées (fallback ultime)
        if df is None:
            try:
                raw_text = content.decode('utf-8', errors='replace')
                from io import StringIO
                df = pd.read_csv(StringIO(raw_text), sep=";", engine='python')
                print(f"✅ Fichier lu en texte avec erreurs ignorées : {file}")
            except Exception as e:
                errors.append(f"lecture texte fallback: {e}")

        if df is not None:
            dataframes.append(df)
        else:
            print(f"❌ Impossible de lire {file}, erreurs: {errors}")

    if not dataframes:
        raise ValueError(f"Aucun fichier valide trouvé dans {prefix}")

    return pd.concat(dataframes, ignore_index=True)




def clean_and_merge(elections, communes, socio_eco):
    elections.columns = elections.columns.str.lower().str.strip()
    communes.columns = communes.columns.str.lower().str.strip()
    socio_eco.columns = socio_eco.columns.str.lower().str.strip()

    # Vérifier présence des colonnes 'code_commune'
    for df_name, df in zip(['elections', 'communes', 'socio_eco'], [elections, communes, socio_eco]):
        if 'code_commune' not in df.columns:
            raise KeyError(f"La colonne 'code_commune' est requise dans le dataset {df_name}")

    communes["code_departement"] = communes["code_commune"].astype(str).str[:2]
    idf_communes = communes[communes["code_departement"].isin(IDF_DEPARTMENTS)]

    merged = elections.merge(idf_communes, on="code_commune", how="inner")
    merged = merged.merge(socio_eco, on="code_commune", how="left")

    if "nombre_votants" in merged.columns and "nombre_inscrits" in merged.columns:
        merged["taux_participation"] = merged["nombre_votants"] / merged["nombre_inscrits"]

    if "voix" in merged.columns and "nombre_votants" in merged.columns:
        merged["resultat_candidat"] = merged["voix"] / merged["nombre_votants"]

    return merged

def main():
    print("✅ Connexion à S3 initialisée avec succès.")
    print("🔄 Lecture des fichiers S3...")
    elections = read_files_from_s3("raw/elections/")
    communes = read_files_from_s3("raw/communes/")
    socio_eco = read_files_from_s3("raw/socio_eco/")

    print("🧠 Fusion et nettoyage...")
    merged_df = clean_and_merge(elections, communes, socio_eco)

    print(f"📊 Dataset final : {merged_df.shape[0]} lignes, {merged_df.shape[1]} colonnes")

    print("✂️ Split train/test...")
    train_df, test_df = train_test_split(merged_df, test_size=0.2, random_state=42)

    os.makedirs("data-test", exist_ok=True)
    train_df.to_parquet("data-test/train.parquet", index=False)
    test_df.to_parquet("data-test/test.parquet", index=False)
    print("✅ Fichiers exportés localement")

    print("☁️ Upload des fichiers vers S3...")
    s3.upload_file("data-test/train.parquet", BUCKET_NAME, "processed/train.parquet")
    print("📤 train.parquet envoyé dans S3.")
    s3.upload_file("data-test/test.parquet", BUCKET_NAME, "processed/test.parquet")
    print("✅ Fichiers uploadés dans S3 → dossier 'processed/'")

if __name__ == "__main__":
    main()
