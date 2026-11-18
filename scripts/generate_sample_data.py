"""Generate SYNTHETIC SportRadar-shaped JSON for offline demos and tests.

All player names, ids and points are invented. The files mirror the structure of
the real endpoints so the same ETL code runs on both. Output: data/sample/.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"
rng = random.Random(42)

COUNTRIES = [  # name, ISO-3, relative weight
    ("United States", "USA", 14), ("France", "FRA", 11), ("Spain", "ESP", 10),
    ("Argentina", "ARG", 9), ("Italy", "ITA", 9), ("Brazil", "BRA", 7),
    ("Great Britain", "GBR", 7), ("Germany", "DEU", 7), ("Croatia", "HRV", 5),
    ("Australia", "AUS", 6), ("Netherlands", "NLD", 5), ("India", "IND", 4),
    ("Japan", "JPN", 4), ("Chile", "CHL", 3), ("Colombia", "COL", 4),
    ("Poland", "POL", 4), ("Czechia", "CZE", 5), ("Canada", "CAN", 4),
    ("Mexico", "MEX", 3), ("Sweden", "SWE", 2), ("El Salvador", "SLV", 1),
]
SURNAMES = ["Alvarez", "Brandt", "Castillo", "Dubois", "Eriksen", "Fontaine", "Garcia",
            "Hartmann", "Ibarra", "Jovanovic", "Kowalski", "Laurent", "Moretti", "Novak",
            "Okafor", "Petrov", "Quintero", "Rossi", "Santos", "Tanaka", "Underwood",
            "Valdez", "Weber", "Xu", "Yilmaz", "Zielinski", "Marin", "Duarte", "Costa", "Lindqvist"]
GIVEN = {
    "men": ["Adrian", "Bruno", "Carlos", "Dario", "Emil", "Felix", "Gabriel", "Hugo", "Ivan",
            "Jonas", "Kai", "Lucas", "Mateo", "Nico", "Oscar", "Pablo", "Rafael", "Sam", "Tomas", "Viktor"],
    "women": ["Alba", "Bianca", "Clara", "Diana", "Elena", "Freya", "Greta", "Hana", "Iris", "Julia",
              "Karla", "Lena", "Marta", "Nadia", "Olga", "Petra", "Rosa", "Sofia", "Tina", "Vera"],
}


def make_competitions() -> dict:
    categories = [("sr:category:3", "ATP"), ("sr:category:6", "WTA"), ("sr:category:785", "ITF Men"),
                  ("sr:category:213", "ITF Women"), ("sr:category:99", "Challenger"),
                  ("sr:category:12", "Davis Cup")]
    items, n = [], 1000
    for cat_id, cat_name in categories:
        for event in range(rng.randint(4, 7)):
            n += 1
            parent_id = f"sr:competition:{n}"
            city = rng.choice(["Vienna", "Santiago", "Lyon", "Tokyo", "Miami", "Basel", "Madrid", "Pune"])
            gender = "women" if "Women" in cat_name or cat_name == "WTA" else "men"
            items.append({"id": parent_id, "name": f"{cat_name} {city} {2026 - event}",
                          "gender": gender, "category": {"id": cat_id, "name": cat_name}})
            for kind in ("singles", "doubles") + (("mixed",) if rng.random() < .3 else ()):
                n += 1
                items.append({"id": f"sr:competition:{n}",
                              "name": f"{cat_name} {city} {kind.title()}",
                              "parent_id": parent_id, "type": kind,
                              "gender": "mixed" if kind == "mixed" else gender,
                              "category": {"id": cat_id, "name": cat_name}})
    return {"generated_at": "2026-11-17T00:00:00+00:00", "competitions": items}


def make_complexes() -> dict:
    spec = [("Nacional", [("Court Central", "Santiago", "Chile", "CHL", "America/Santiago"),
                          ("Court Andes", "Santiago", "Chile", "CHL", "America/Santiago")]),
            ("Stadthalle Complex", [("Stadthalle", "Vienna", "Austria", "AUT", "Europe/Vienna")]),
            ("Roland Park", [("Court Philippe", "Paris", "France", "FRA", "Europe/Paris"),
                             ("Court Suzanne", "Paris", "France", "FRA", "Europe/Paris"),
                             ("Court Simonne", "Paris", "France", "FRA", "Europe/Paris")]),
            ("Flushing Grounds", [("Arena Grande", "New York", "United States", "USA", "America/New_York")]),
            ("Melbourne Park", [("Rod Arena", "Melbourne", "Australia", "AUS", "Australia/Melbourne"),
                                ("Margaret Court", "Melbourne", "Australia", "AUS", "Australia/Melbourne")]),
            ("Foro Italico", [("Centrale", "Rome", "Italy", "ITA", "Europe/Rome")]),
            ("Caja Magica", [("Manolo Santana", "Madrid", "Spain", "ESP", "Europe/Madrid"),
                             ("Court Two", "Madrid", "Spain", "ESP", "Europe/Madrid")]),
            ("Ariake Colosseum", [("Colosseum", "Tokyo", "Japan", "JPN", "Asia/Tokyo")]),
            ("Balewadi Sports", [("Mahalunge Court", "Pune", "India", "IND", "Asia/Kolkata")]),
            ("Club Zagreb", [("Dom Sportova", "Zagreb", "Croatia", "HRV", "Europe/Zagreb")])]
    out, v = [], 5000
    for i, (name, venues) in enumerate(spec, start=1):
        rows = []
        for vname, city, country, code, tz in venues:
            v += 1
            rows.append({"id": f"sr:venue:{v}", "name": vname, "city_name": city,
                         "country_name": country, "country_code": code, "timezone": tz})
        out.append({"id": f"sr:complex:{i}", "name": name, "venues": rows})
    return {"generated_at": "2026-11-17T00:00:00+00:00", "complexes": out}


def make_ranking(tour: str, type_id: int, gender: str, size: int, id_start: int) -> dict:
    countries, weights = zip(*[((c, code), w) for c, code, w in COUNTRIES])
    rows, rank, i = [], 1, 0
    points = 8200
    while len(rows) < size:
        country, code = rng.choices(countries, weights)[0]
        given, sur = rng.choice(GIVEN[gender]), rng.choice(SURNAMES)
        name = f"{sur}, {given}"
        points = max(60, int(points * rng.uniform(0.9885, 0.9985)))
        movement = 0 if rng.random() < .38 else rng.randint(-6, 6)
        i += 1
        rows.append({"rank": rank, "movement": movement, "points": points,
                     "competitions_played": rng.randint(8, 34),
                     "competitor": {"id": f"sr:competitor:{id_start + i}", "name": name,
                                    "country": country, "country_code": code,
                                    "abbreviation": (sur[:3]).upper()}})
        rank += 1
    # Real doubles feeds list partners with identical points; mimic a few ties.
    for a, b in zip(rows[0:30:2], rows[1:30:2]):
        if rng.random() < .5:
            b["points"], b["rank"] = a["points"], a["rank"]
    return {"type_id": type_id, "name": tour, "year": 2026, "week": 46,
            "gender": gender, "competitor_rankings": rows}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payloads = {
        "competitions.json": make_competitions(),
        "complexes.json": make_complexes(),
        "doubles_rankings.json": {
            "generated_at": "2026-11-16T21:50:25+00:00",
            "rankings": [make_ranking("ATP", 2, "men", 300, 100000),
                         make_ranking("WTA", 4, "women", 300, 200000)],
        },
    }
    for filename, payload in payloads.items():
        (OUT / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote data/sample/{filename}")


if __name__ == "__main__":
    main()
