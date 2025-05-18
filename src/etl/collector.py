import os
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL', 'https://www.data.gouv.fr')
RAW_DIR  = os.path.abspath(os.path.join(os.getcwd(), 'data', 'raw'))

# Extensions ciblées
FILE_EXTS = ('.csv', '.json', '.xls', '.xlsx', '.zip', '.shp', '.parquet')

# Pages thématiques
PAGES = [
    'https://www.data.gouv.fr/fr/pages/donnees-des-elections/',
    'https://www.data.gouv.fr/fr/pages/donnees-securite/',
    'https://www.data.gouv.fr/fr/pages/donnees-emploi/',
    'https://www.data.gouv.fr/fr/organizations/institut-national-de-la-statistique-et-des-etudes-economiques-insee/'
]

class DataCollector:
    def __init__(self):
        os.makedirs(RAW_DIR, exist_ok=True)

    def find_dataset_pages(self, page_url: str) -> set[str]:
        r = requests.get(page_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        return {
            urljoin(BASE_URL, a['href']).split('?')[0]
            for a in soup.find_all('a', href=True)
            if '/fr/datasets/' in a['href']
        }

    def find_resource_links(self, dataset_url: str) -> set[str]:
        r = requests.get(dataset_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        return {
            (href if href.startswith('http') else urljoin(BASE_URL, href)).split('?')[0]
            for a in soup.find_all('a', href=True)
            for href in [a['href']]
            if any(href.lower().endswith(ext) for ext in FILE_EXTS)
        }

    def download_file(self, url: str, dest_dir: str):
        os.makedirs(dest_dir, exist_ok=True)
        fname = os.path.basename(urlparse(url).path)
        path = os.path.join(dest_dir, fname)
        if os.path.exists(path):
            print(f"→ Ignoré {fname}")
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
                print(f"⚠️ Erreur {e}, nouvel essai dans 5 s…")
                time.sleep(5)
        print(f"❌ Échec de {fname}")

    def collect(self):
        all_resources = set()
        for page in PAGES:
            ds_pages = self.find_dataset_pages(page)
            print(f"[{page}] → {len(ds_pages)} pages de datasets trouvées")
            time.sleep(2)
            for ds in ds_pages:
                res_links = self.find_resource_links(ds)
                print(f"  • {len(res_links)} fichiers détectés sur {ds}")
                all_resources.update(res_links)
                time.sleep(1)

        print(f"Total à télécharger : {len(all_resources)} fichiers")
        for url in sorted(all_resources):
            # classification simple selon extension
            ext = os.path.splitext(urlparse(url).path)[1].lstrip('.').lower() or 'other'
            dest = os.path.join(RAW_DIR, ext)
            self.download_file(url, dest)
            time.sleep(1)

if __name__ == '__main__':
    collector = DataCollector()
    collector.collect()
    print("\n✅ Collecte terminée. Fichiers dans:", RAW_DIR)
