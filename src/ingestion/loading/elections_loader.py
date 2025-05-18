from .base_loader import BaseLoader
import pandas as pd, requests, io, faker

class ElectionsAPILoader(BaseLoader):
    def load(self):
        resp = requests.get(self.cfg["url"], timeout=30)
        return pd.read_csv(io.StringIO(resp.text), sep=";")

class ElectionsFakeLoader(BaseLoader):
    def load(self):
        fake = faker.Faker("fr_FR")
        rows = []
        for _ in range(self.cfg["fake_rows"]):
            rows.append({
                "code_commune": fake.postcode(),
                "candidat": fake.last_name(),
                "voix": fake.random_int(0, 1000),
                "tour": fake.random_element(elements=(1, 2)),
                "annee": fake.random_element(elements=(2012, 2017, 2022)),
            })
        return pd.DataFrame(rows)
