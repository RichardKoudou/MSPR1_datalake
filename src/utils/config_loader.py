import os
import yaml

def load_config():
    # Récupère le chemin absolu du fichier actuel (src/utils/config_loader.py)
    current_dir = os.path.dirname(__file__)

    # Remonte jusqu'à la racine du projet (Scrapping/)
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

    # Construit le chemin absolu vers config.yml à la racine
    config_path = os.path.join(project_root, "config.yml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Le fichier config.yml est introuvable à : {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

