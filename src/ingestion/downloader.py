import os
import requests
import zipfile
from io import BytesIO

def download_and_extract(url, output_folder):
    print(f"Téléchargement depuis : {url}")
    os.makedirs(output_folder, exist_ok=True)

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erreur HTTP {response.status_code} pour l'URL : {url}")

    content_type = response.headers.get('Content-Type', '')
    if 'zip' in content_type or url.endswith('.zip'):
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(output_folder)
            print(f"ZIP extrait dans : {output_folder}")
    else:
        filename = os.path.join(output_folder, url.split('/')[-1])
        with open(filename, 'wb') as f:
            f.write(response.content)
            print(f"Fichier téléchargé : {filename}")
