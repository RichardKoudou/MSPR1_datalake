import csv
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker('fr_FR')

def gen_communes(n=100):
    communes = []
    for _ in range(n):
        code = fake.postcode().replace(' ', '')[:5]
        communes.append({
            'insee_code': code,
            'name': fake.city(),
            'department': code[:2],
            'region': fake.region()
        })
    return communes

def gen_socio_economic(communes, years=[2020, 2021, 2022]):
    rows = []
    for c in communes:
        for y in years:
            rows.append({
                'insee_code': c['insee_code'],
                'year': y,
                'unemployment': round(random.uniform(5, 15), 2),
                'median_income': round(random.uniform(15000, 35000), 2),
                'education_index': round(random.uniform(0.5, 1.0), 2)
            })
    return rows

def gen_parties():
    return [
        {'name': 'Parti Alpha', 'abbreviation': 'PA'},
        {'name': 'Parti Beta',  'abbreviation': 'PB'},
        {'name': 'Parti Gamma', 'abbreviation': 'PG'},
    ]

def gen_elections(communes, start_date=date(2020,1,1), count=10):
    elections = []
    for _ in range(count):
        c = random.choice(communes)
        d = start_date + timedelta(days=random.randint(0, 365*3))
        elections.append({
            'insee_code': c['insee_code'],
            'election_date': d,
            'election_type': random.choice(['municipales','regionale','legislative']),
            'turnout_rate': round(random.uniform(40, 85),2)
        })
    return elections

def gen_results(elections, parties):
    results = []
    for idx, e in enumerate(elections, start=1):
        total_votes = random.randint(500, 5000)
        shares = [random.random() for _ in parties]
        s = sum(shares)
        for party, share in zip(parties, shares):
            votes = int(total_votes * share / s)
            results.append({
                'election_id': idx,
                'party_id': parties.index(party) + 1,
                'votes': votes,
                'vote_pct': round(votes/total_votes*100,2)
            })
    return results

if __name__ == '__main__':
    communes = gen_communes(200)
    socio  = gen_socio_economic(communes)
    parties= gen_parties()
    elections = gen_elections(communes, count=300)
    results   = gen_results(elections, parties)

    # Sauvegarde CSV dans data/fake
    for name, data in [
        ('communes.csv', communes),
        ('socio_eco.csv', socio),
        ('election.csv', elections),
    ]:
        keys = data[0].keys()
        with open(f'../../data/fake/{name}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    # Pour parties et results, mieux en base via loader.py
    print("Fichiers factices générés dans data/fake/")
