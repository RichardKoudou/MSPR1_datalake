import os
import boto3
from botocore.exceptions import NoCredentialsError

# Configuration de MinIO
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "election-datalake"
LOCAL_FOLDER = "election_dataset"

# Connexion à MinIO avec boto3
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Création du bucket s'il n'existe pas
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' créé avec succès.")
except Exception as e:
    print(f"Le bucket existe peut-être déjà : {e}")

# Fonction pour envoyer les fichiers vers MinIO
def upload_files_to_minio():
    for root, _, files in os.walk(LOCAL_FOLDER):
        for file in files:
            file_path = os.path.join(root, file)
            object_name = file  # Nom du fichier dans MinIO
            
            try:
                s3_client.upload_file(file_path, BUCKET_NAME, object_name)
                print(f"Le fichier {file} a été envoyé vers MinIO avec succès !")
            except NoCredentialsError:
                print("Erreur : Vérifiez les identifiants MinIO.")
            except Exception as e:
                print(f"Échec du transfert de {file} : {e}")

# Lancer l'upload
upload_files_to_minio()
