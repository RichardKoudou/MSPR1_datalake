import requests
from bs4 import BeautifulSoup
import os
import re
import time

def get_all_election_datasets():
    base_url = "https://www.data.gouv.fr"
    elections_url = "https://www.data.gouv.fr/fr/pages/donnees-emploi/"
    try:
        response = requests.get(elections_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de l'accès au site : {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    dataset_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.search(r'/fr/datasets/', href):
            full_link = href if href.startswith("http") else base_url + href
            dataset_links.append(full_link)
    
    return dataset_links

def download_dataset_files(dataset_url, save_dir):
    try:
        response = requests.get(dataset_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de l'accès à {dataset_url} : {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    file_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if re.search(r'\.(csv|json|xls|xlsx|zip)$', href):
            full_link = href if href.startswith("http") else f"https:{href}" if href.startswith("//") else base_url + href
            file_links.append(full_link)
    
    os.makedirs(save_dir, exist_ok=True)
    
    for file_link in file_links:
        file_name = file_link.split("/")[-1]
        file_path = os.path.join(save_dir, file_name)
        
        print(f"Téléchargement de {file_name} depuis {file_link}...")
        for attempt in range(3):  # Retry jusqu'à 3 fois
            try:
                file_response = requests.get(file_link, stream=True, timeout=15)
                file_response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=1024):
                        f.write(chunk)
                print(f"Téléchargé : {file_name}")
                time.sleep(2)  # Pause plus longue
                break
            except requests.RequestException as e:
                print(f"Tentative {attempt + 1} échouée pour {file_name} : {e}")
                time.sleep(5)  # Pause avant retry
        else:
            print(f"Échec final du téléchargement de {file_name}")

if __name__ == "__main__":
    datasets = get_all_election_datasets()
    print(f"{len(datasets)} datasets trouvés.")
    
    save_directory = "election_dataset"
    for dataset in datasets:
        download_dataset_files(dataset, save_directory)