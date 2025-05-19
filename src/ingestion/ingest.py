import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.config_loader import load_config

import yaml
from src.ingestion.downloader import download_and_extract
from src.ingestion.uploader import upload_folder_to_s3

def run_ingestion():
    config = load_config()
    aws_cfg = config["aws"]
    for dataset_cfg in config["datasets"]:
        dataset_name = dataset_cfg["name"]
        urls = dataset_cfg["urls"]
        local_folder = os.path.join("data", dataset_name)
        os.makedirs(local_folder, exist_ok=True)

        print(f"Téléchargement du dataset : {dataset_name}")
        for url in urls:
            print(f"Téléchargement depuis : {url}")
            download_and_extract(url, local_folder)

        s3_prefix = f"raw/{dataset_name}/"
        print(f"Upload des fichiers vers s3://{aws_cfg['bucket']}/{s3_prefix}")
        upload_folder_to_s3(local_folder, aws_cfg["bucket"], s3_prefix, aws_cfg)



if __name__ == "__main__":
    run_ingestion()
