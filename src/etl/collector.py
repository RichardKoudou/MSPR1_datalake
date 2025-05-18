import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# URL de base pour data.gouv.fr
BASE_URL = os.getenv('BASE_URL', 'https://www.data.gouv.fr')

# Répertoire de destination pour les données brutes (à la racine du projet)
DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
)
# Création du répertoire data/raw s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Extensions ciblées pour les ressources
FILE_EXTS = ('.csv', '.json', '.xls', '.xlsx', '.zip', '.shp', '.parquet')

# Pages thématiques à scraper
PAGES = [
    'https://www.data.gouv.fr/fr/pages/donnees-des-elections/',
    'https://www.data.gouv.fr/fr/pages/donnees-securite/',
    'https://www.data.gouv.fr/fr/pages/donnees-emploi/',
    'https://www.data.gouv.fr/fr/organizations/institut-national-de-la-statistique-et-des-etudes-economiques-insee/'
]

class DataCollector:
    """Collecte et stocke localement les fichiers bruts depuis data.gouv.fr."""

    def __init__(self):
        # Répertoire principal des données brutes
        self.data_dir = DATA_DIR

    def find_dataset_pages(self, page_url: str) -> set[str]:
        """Récupère les URLs de pages de datasets (/fr/datasets/) depuis une page thématique."""
        try:
            resp = requests.get(page_url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Erreur lors de l'accès à {page_url}: {e}")
            return set()

        soup = BeautifulSoup(resp.text, 'html.parser')
        pages = {
            urljoin(BASE_URL, a['href']).split('?')[0]
            for a in soup.find_all('a', href=True)
            if '/fr/datasets/' in a['href']
        }
        print(f"[{page_url}] → {len(pages)} pages de datasets trouvées")
        return pages

    def find_resource_links(self, dataset_url: str) -> set[str]:
        """Extrait les liens directs vers les fichiers (.csv, .zip, etc.) depuis une page de dataset."""
        try:
            resp = requests.get(dataset_url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Erreur lors de l'accès à {dataset_url}: {e}")
            return set()

        soup = BeautifulSoup(resp.text, 'html.parser')
        files = {
            (href if href.startswith('http') else urljoin(BASE_URL, href)).split('?')[0]
            for a in soup.find_all('a', href=True)
            for href in [a['href']]
            if any(href.lower().endswith(ext) for ext in FILE_EXTS)
        }
        print(f"  • {len(files)} fichiers détectés sur {dataset_url}")
        return files

    def download_file(self, url: str, dest_dir: str):
        """Télécharge un fichier et le sauvegarde localement dans dest_dir, avec retries."""
        os.makedirs(dest_dir, exist_ok=True)
        fname = os.path.basename(urlparse(url).path)
        path = os.path.join(dest_dir, fname)
        if os.path.exists(path):
            print(f"→ Ignoré {fname} (existe déjà)")
            return

        for attempt in range(1, 4):
            try:
                print(f"↓ Téléchargement {fname} (essai {attempt})…")
                with requests.get(url, stream=True, timeout=20) as resp:
                    resp.raise_for_status()
                    with open(path, 'wb') as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)
                print(f"✔ Enregistré {path}")
                return
            except Exception as e:
                print(f"⚠️ Erreur {e}, nouvel essai dans 5 s…")
                time.sleep(5)
        print(f"❌ Échec du téléchargement de {fname}")

    def collect(self):
        """Exécute la collecte multi-étapes: pages thématiques → pages datasets → fichiers."""
        all_resources = set()
        for page in PAGES:
            ds_pages = self.find_dataset_pages(page)
            time.sleep(2)
            for ds in ds_pages:
                res_links = self.find_resource_links(ds)
                all_resources.update(res_links)
                time.sleep(1)

        print(f"Total à télécharger : {len(all_resources)} fichiers")
        for url in sorted(all_resources):
            ext = os.path.splitext(urlparse(url).path)[1].lstrip('.').lower() or 'other'
            dest = os.path.join(self.data_dir, ext)
            self.download_file(url, dest)
            time.sleep(1)

if __name__ == '__main__':
    collector = DataCollector()
    collector.collect()
    print("\n✅ Collecte terminée. Fichiers dans:", DATA_DIR)
