import os
import requests
import pandas as pd
from dotenv import load_dotenv
from io import BytesIO
from bs4 import BeautifulSoup
import re
import time

class DataCollector:
    """Classe pour la collecte des données depuis data.gouv.fr"""

    def __init__(self):
        load_dotenv()
        self.base_url = "https://www.data.gouv.fr"
        self.supported_extensions = ['csv', 'json', 'xls', 'xlsx', 'zip']

    def get_all_datasets(self, url):
        """Récupère tous les liens des datasets depuis une URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            dataset_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if re.search(r'/fr/datasets/', href):
                    full_link = href if href.startswith("http") else self.base_url + href
                    dataset_links.append(full_link)
            
            return dataset_links
        except requests.RequestException as e:
            print(f"Erreur lors de l'accès au site : {e}")
            return []

    def download_dataset_files(self, dataset_url):
        """Télécharge les fichiers d'un dataset et les organise par type"""
        try:
            response = requests.get(dataset_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            file_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(href.lower().endswith(ext) for ext in self.supported_extensions):
                    full_link = href if href.startswith("http") else f"https:{href}" if href.startswith("//") else self.base_url + href
                    file_links.append(full_link)
            
            for file_link in file_links:
                self._download_file(file_link)
                time.sleep(2)  # Pause entre les téléchargements
                
        except requests.RequestException as e:
            print(f"Erreur lors de l'accès à {dataset_url} : {e}")

    def _download_file(self, file_link):
        """Télécharge un fichier et le sauvegarde dans le dossier approprié"""
        file_name = file_link.split("/")[-1]
        file_ext = file_name.split(".")[-1].lower()
        
        # Création du dossier spécifique au type de fichier
        save_dir = os.path.join('data/raw', file_ext)
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, file_name)
        
        print(f"Téléchargement de {file_name} depuis {file_link}...")
        for attempt in range(3):  # Retry jusqu'à 3 fois
            try:
                response = requests.get(file_link, stream=True, timeout=15)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"Téléchargé : {file_name}")
                break
            except requests.RequestException as e:
                print(f"Tentative {attempt + 1} échouée pour {file_name} : {e}")
                time.sleep(5)  # Pause avant retry
        else:
            print(f"Échec final du téléchargement de {file_name}")

    def collect_all_data(self, urls):
        """Collecte toutes les données à partir d'une liste d'URLs"""
        for url in urls:
            datasets = self.get_all_datasets(url)
            print(f"{len(datasets)} datasets trouvés pour {url}")
            
            for dataset in datasets:
                self.download_dataset_files(dataset)
                time.sleep(2)  # Pause entre les datasets

# Exemple d'utilisation
if __name__ == "__main__":
    collector = DataCollector()
    urls = [
        "https://www.data.gouv.fr/fr/pages/donnees-emploi/",
        "https://www.data.gouv.fr/fr/pages/donnees-elections/",
        "https://www.data.gouv.fr/fr/pages/donnees-securite/"
        # Ajoutez d'autres URLs sources ici
    ]
    collector.collect_all_data(urls)