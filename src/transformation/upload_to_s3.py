# src/etl/upload_to_s3.py

import os
import logging
import boto3
from botocore.exceptions import ClientError            # OK pour toutes les erreurs S3
# from boto3.exceptions import S3UploadFailedError     # Optionnel, si vous voulez distinguer

from dotenv import load_dotenv

# Charger les credentials AWS
load_dotenv()

AWS_REGION     = os.getenv('AWS_REGION', 'us-east-1')
BUCKET_NAME    = os.getenv('S3_BUCKET_NAME', 'mon-bucket-s3')
LOCAL_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data')
)

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def upload_directory_to_s3(local_directory: str, bucket: str, s3_prefix: str = ''):
    """
    Upload récursif de `local_directory` vers `bucket`, 
    en ignorant les fichiers cachés et en gérant les erreurs.
    """
    s3 = boto3.client('s3', region_name=AWS_REGION)

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # Ignorer les fichiers cachés (ex. .gitkeep)
            if filename.startswith('.'):
                logger.debug(f"Ignoré (caché) : {filename}")
                continue

            local_path = os.path.join(root, filename)
            # Recréer la structure dans S3
            rel_path = os.path.relpath(local_path, local_directory)
            s3_key = os.path.join(s3_prefix, rel_path).replace(os.sep, '/')

            try:
                logger.info(f"Uploading {local_path} → s3://{bucket}/{s3_key}")
                s3.upload_file(local_path, bucket, s3_key)
                logger.info(f"✔ Uploaded {s3_key}")
            except ClientError as e:
                # Couvre tous les cas (AccessDenied, etc.) :contentReference[oaicite:1]{index=1}
                logger.error(f"❌ Échec upload {s3_key}: {e}")
                continue

    logger.info("✅ Upload terminé.")

if __name__ == '__main__':
    upload_directory_to_s3(LOCAL_DATA_DIR, BUCKET_NAME)
