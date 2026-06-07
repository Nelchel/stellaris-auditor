#!/usr/bin/env python3

import json
import re
import sys
import zipfile
import zlib
from pathlib import Path
from datetime import datetime


RESOURCES = {
    "energy", "minerals", "food", "alloys", "consumer_goods",
    "unity", "influence", "physics_research", "society_research",
    "engineering_research", "trade", "rare_crystals", "volatile_motes",
    "exotic_gases", "minor_artifacts", "astral_threads"
}


META_BENCHMARKS = {
    2230: {
        "research": 120,
        "military_power": 1500,
        "economy_core": 300,
    },
    2250: {
        "research": 250,
        "military_power": 4000,
        "economy_core": 600,
    },
    2275: {
        "research": 500,
        "military_power": 8000,
        "economy_core": 1200,
    },
    2300: {
        "research": 1000,
        "military_power": 20000,
        "economy_core": 2500,
    },
    2325: {
        "research": 1800,
        "military_power": 45000,
        "economy_core": 4500,
    },
}


def extract_save_year(save_path: str) -> int | None:
    match = re.search(r'(\d{4})\.', save_path)
    if match:
        return int(match.group(1))
    return None


def find_closest_benchmark(year: int) -> tuple[int, dict]:
    years = sorted(META_BENCHMARKS.keys())
    closest = min(years, key=lambda benchmark_year: abs(benchmark_year - year))
    return closest, META_BENCHMARKS[closest]


def benchmark_position(value: float, benchmark: float) -> str:
    if benchmark <= 0:
        return "Unknown"

    ratio = value / benchmark

    if ratio >= 1.5:
        return "Far Ahead"
    if ratio >= 1.15:
        return "Ahead"
    if ratio >= 0.85:
        return "On Curve"
    if ratio >= 0.6:
        return "Behind"
    return "Far Behind"


def build_meta_benchmarking(audit: dict) -> dict:
    save_year = extract_save_year(audit["save"])

    if not save_year:
        return {
            "error": "Impossible d’extraire l’année depuis le nom de la save.",
        }

    benchmark_year, benchmark = find_closest_benchmark(save_year)

    metrics = audit.get("metrics", {})
    resources = audit.get("resources", {})
    income = resources.get("income", {})

    research = metrics.get("research", {}).get("research_total", 0)
    military = metrics.get("military", {}).get("military_power", 0)
    economy_core = (
        income.get("energy", 0)
        + income.get("minerals", 0)
        + income.get("food", 0)
        + income.get("alloys", 0)
        + income.get("consumer_goods", 0)
    )

    research_curve = benchmark_position(research, benchmark["research"])
    military_curve = benchmark_position(military, benchmark["military_power"])
    economy_curve = benchmark_position(economy_core, benchmark["economy_core"])

    ratio = lambda value, target: round(value / target, 3) if target else None

    signals = []
    if economy_curve in {"Ahead", "Far Ahead"}:
        signals.append("économiquement en avance")
    elif economy_curve in {"Behind", "Far Behind"}:
        signals.append("économiquement en retard")

    if research_curve in {"Behind", "Far Behind"}:
        signals.append("scientifiquement en retard")
    elif research_curve in {"Ahead", "Far Ahead"}:
        signals.append("scientifiquement en avance")

    if military_curve in {"Ahead", "Far Ahead"}:
        signals.append("militairement solide")
    elif military_curve in {"Behind", "Far Behind"}:
        signals.append("militairement fragile")

    if signals:
        overall = ", ".join(signals).capitalize() + "."
    else:
        overall = "Globalement dans la courbe attendue."

    return {
        "save_year": save_year,
        "benchmark_reference_year": benchmark_year,
        "benchmarks": benchmark,
        "actual_values": {
            "research": round(research, 2),
            "military_power": round(military, 2),
            "economy_core": round(economy_core, 2),
        },
        "ratios": {
            "research_ratio": ratio(research, benchmark["research"]),
            "military_ratio": ratio(military, benchmark["military_power"]),
            "economy_ratio": ratio(economy_core, benchmark["economy_core"]),
        },
        "research_curve": research_curve,
        "military_curve": military_curve,
        "economy_curve": economy_curve,
        "overall_meta_position": overall,
        "note": "Benchmarks heuristiques, pensés pour donner une tendance, pas une vérité absolue. À calibrer selon difficulté, mods et style de jeu.",
    }


def read_meta(save_path: Path) -> str:
    with zipfile.ZipFile(save_path, "r") as z:
        if "meta" not in z.namelist():
            return ""
        return z.read("meta").decode("utf-8", errors="ignore")


def read_save(save_path: Path) -> str:
    with zipfile.ZipFile(save_path, "r") as z:
        if "gamestate" not in z.namelist():
            raise ValueError("Impossible de trouver 'gamestate'.")

        raw = z.read("gamestate")

        try:
            text = raw.decode("utf-8")
            if "country" in text or "player" in text:
                return text
        except UnicodeDecodeError:
            pass

        try:
            return zlib.decompress(raw).decode("utf-8", errors="ignore")
        except Exception as e:
            raise ValueError(f"Impossible de décoder gamestate : {e}")


def extract_block(text: str, start_pattern: str) -> str | None:
    match = re.search(start_pattern, text)
    if not match:
        return None

    start = match.end() - 1
    depth = 0

    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]

    return None


def find_country_id_from_meta(save_path: Path) -> str | None:
    meta = read_meta(save_path)

    patterns = [
        r'player_country\s*=\s*(\d+)',
        r'local_player_country\s*=\s*(\d+)',
        r'country\s*=\s*(\d+)',
        r'player\s*=\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, meta)
        if match:
            return match.group(1)

    return None


def find_player_country_id(text: str) -> str | None:
    patterns = [
        r'player_country\s*=\s*(\d+)',
        r'local_player_country\s*=\s*(\d+)',
        r'human\s*=\s*\{\s*country\s*=\s*(\d+)',
        r'player\s*=\s*\{\s*\{\s*name\s*=\s*"[^"]*"\s*country\s*=\s*(\d+)',
        r'player\s*=\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)

    return None


def extract_country_block(text: str, country_id: str) -> str | None:
    country_section = extract_block(text, r'\bcountry\s*=\s*\{')
    if not country_section:
        return None

    return extract_block(
        country_section,
        rf'\b{re.escape(country_id)}\s*=\s*\{{'
    )


def extract_number(block: str, key: str, default: float = 0.0) -> float:
    match = re.search(
        rf'\b{re.escape(key)}\s*=\s*([-+]?\d+(?:\.\d+)?)',
        block
    )
    if not match:
        return default
    return float(match.group(1))


def extract_resource_values_sum(block: str) -> dict:
    resources = {}

    pattern_direct = r'\b([a-zA-Z0-9_]+)\s*=\s*([-+]?\d+(?:\.\d+)?)'

    for key, value in re.findall(pattern_direct, block):
        if key in RESOURCES:
            resources[key] = resources.get(key, 0) + float(value)

    return resources


def extract_stockpile(country_block: str) -> dict:
    block = extract_block(country_block, r'\bresources\s*=\s*\{')
    if not block:
        return {}

    resources = {}

    pattern_amount = r'\b([a-zA-Z0-9_]+)\s*=\s*\{\s*amount\s*=\s*([-+]?\d+(?:\.\d+)?)'

    for key, value in re.findall(pattern_amount, block):
        if key in RESOURCES:
            resources[key] = float(value)

    pattern_direct = r'\b([a-zA-Z0-9_]+)\s*=\s*([-+]?\d+(?:\.\d+)?)'

    for key, value in re.findall(pattern_direct, block):
        if key in RESOURCES and key not in resources:
            resources[key] = float(value)

    return resources


def extract_budget(country_block: str) -> tuple[dict, dict]:
    budget_block = extract_block(country_block, r'\bbudget\s*=\s*\{')
    if not budget_block:
        return {}, {}

    current_month = extract_block(budget_block, r'\bcurrent_month\s*=\s*\{')
    if not current_month:
        return {}, {}

    income_block = extract_block(current_month, r'\bincome\s*=\s*\{')
    expenses_block = (
        extract_block(current_month, r'\bexpenses\s*=\s*\{')
        or extract_block(current_month, r'\bexpense\s*=\s*\{')
    )

    income = extract_resource_values_sum(income_block or "")
    expenses = extract_resource_values_sum(expenses_block or "")

    return income, expenses


def count_occurrences(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def clamp(value: float, min_value=0, max_value=100) -> int:
    return int(max(min_value, min(max_value, round(value))))


def get_value(primary: dict, fallback: dict, key: str) -> float:
    value = primary.get(key)
    if value is not None and value != 0:
        return value
    return fallback.get(key, 0)


def build_metrics(country_block: str, gamestate: str, stockpile: dict, income: dict, expenses: dict) -> dict:
    physics = get_value(income, stockpile, "physics_research")
    society = get_value(income, stockpile, "society_research")
    engineering = get_value(income, stockpile, "engineering_research")
    research_total = physics + society + engineering

    empire_size = extract_number(country_block, "empire_size", 0)

    fleet_size = extract_number(country_block, "fleet_size", 0)
    used_naval_capacity = extract_number(country_block, "used_naval_capacity", 0)
    military_power = extract_number(country_block, "military_power", 0)
    economy_power = extract_number(country_block, "economy_power", 0)
    tech_power = extract_number(country_block, "tech_power", 0)

    naval_ratio = None
    if fleet_size > 0:
        naval_ratio = round(used_naval_capacity / fleet_size, 3)

    research_density = None
    if empire_size > 0:
        research_density = round(research_total / empire_size, 3)

    return {
        "parser_status": {
            "income_found": bool(income),
            "expenses_found": bool(expenses),
            "version_note": "V1.3 lit budget.current_month.income au lieu de monthly_income."
        },
        "economy": {
            "energy_stock": stockpile.get("energy", 0),
            "minerals_stock": stockpile.get("minerals", 0),
            "food_stock": stockpile.get("food", 0),
            "alloys_stock": stockpile.get("alloys", 0),
            "consumer_goods_stock": stockpile.get("consumer_goods", 0),
            "energy_income": income.get("energy", 0),
            "minerals_income": income.get("minerals", 0),
            "food_income": income.get("food", 0),
            "alloys_income": income.get("alloys", 0),
            "consumer_goods_income": income.get("consumer_goods", 0),
            "unity_income": income.get("unity", 0),
            "influence_income": income.get("influence", 0),
            "trade_income": income.get("trade", 0),
            "energy_expense": expenses.get("energy", 0),
            "minerals_expense": expenses.get("minerals", 0),
            "food_expense": expenses.get("food", 0),
            "alloys_expense": expenses.get("alloys", 0),
            "consumer_goods_expense": expenses.get("consumer_goods", 0),
        },
        "research": {
            "physics_income": physics,
            "society_income": society,
            "engineering_income": engineering,
            "research_total": research_total,
            "research_density": research_density,
        },
        "military": {
            "fleet_size": fleet_size,
            "used_naval_capacity": used_naval_capacity,
            "naval_ratio": naval_ratio,
            "military_power": military_power,
            "alloys_income": income.get("alloys", 0),
            "alloys_stock": stockpile.get("alloys", 0),
        },
        "empire": {
            "empire_size": empire_size,
            "economy_power": economy_power,
            "tech_power": tech_power,
        },
        "stability_raw_global": {
            "unemployment_occurrences_global": count_occurrences(gamestate, r'unemployed\s*=\s*yes'),
            "high_crime_occurrences_global": count_occurrences(gamestate, r'crime\s*=\s*[7-9]\d'),
            "low_stability_occurrences_global": count_occurrences(gamestate, r'stability\s*=\s*[0-3]\d'),
            "note": "Encore global à toute la save. V1.4 devra analyser uniquement tes planètes."
        }
    }


def score_economy(stockpile: dict, income: dict):
    score = 60
    warnings = []

    if not income:
        score -= 15
        warnings.append("Revenus mensuels introuvables.")
        return clamp(score), warnings

    for res in ["energy", "minerals", "food", "alloys", "consumer_goods"]:
        value = income.get(res, 0)
        if value < 0:
            score -= 15
            warnings.append(f"Déficit en {res}: {value:.1f}/mois.")

    alloys_income = income.get("alloys", 0)
    minerals_income = income.get("minerals", 0)
    energy_income = income.get("energy", 0)
    consumer_goods_income = income.get("consumer_goods", 0)

    if energy_income > 300:
        score += 12
    if minerals_income > 200:
        score += 8
    if alloys_income > 60:
        score += 15
    elif alloys_income < 25:
        score -= 15
        warnings.append("Production d’alliages faible.")

    if consumer_goods_income > 80:
        score += 8
    elif consumer_goods_income < 10:
        score -= 8
        warnings.append("Production de biens de consommation faible.")

    if stockpile.get("alloys", 0) < 200:
        score -= 8
        warnings.append("Stock d’alliages bas.")

    return clamp(score), warnings


def score_research(income: dict, stockpile: dict, empire_size: float):
    physics = get_value(income, stockpile, "physics_research")
    society = get_value(income, stockpile, "society_research")
    engineering = get_value(income, stockpile, "engineering_research")
    total = physics + society + engineering

    score = 50 + total / 18
    warnings = []

    if empire_size > 0:
        density = total / empire_size
        if density < 1:
            score -= 20
            warnings.append("Recherche très faible par rapport à la taille de l’empire.")
        elif density < 2:
            score -= 10
            warnings.append("Recherche un peu faible par rapport à la taille de l’empire.")
        elif density > 4:
            score += 12

    if total < 250:
        warnings.append("Sortie scientifique basse.")
    elif total > 500:
        score += 10

    return clamp(score), warnings


def score_military(country_block: str, income: dict, stockpile: dict):
    fleet_size = extract_number(country_block, "fleet_size", 0)
    used_naval_capacity = extract_number(country_block, "used_naval_capacity", 0)
    military_power = extract_number(country_block, "military_power", 0)
    alloys_income = income.get("alloys", 0)
    alloys_stock = stockpile.get("alloys", 0)

    score = 50
    warnings = []

    if military_power > 20000:
        score += 25
    elif military_power > 10000:
        score += 15
    elif military_power < 5000:
        score -= 15
        warnings.append("Puissance militaire faible.")

    if fleet_size > 0:
        ratio = used_naval_capacity / fleet_size
        if ratio >= 0.9:
            score += 10
        elif ratio < 0.5:
            score -= 15
            warnings.append("Capacité navale sous-utilisée.")

    if alloys_income > 60:
        score += 10
    elif alloys_income < 25:
        score -= 10
        warnings.append("Production d’alliages faible pour soutenir la flotte.")

    if alloys_stock < 200:
        score -= 8
        warnings.append("Stock d’alliages bas pour reconstruire après une guerre.")

    return clamp(score), warnings


def score_expansion(country_block: str):
    empire_size = extract_number(country_block, "empire_size", 0)

    score = 60
    warnings = []

    if empire_size < 100:
        score -= 15
        warnings.append("Empire encore petit.")
    elif empire_size > 300:
        score += 10

    return clamp(score), warnings


def extract_owned_planet_ids(country_block: str) -> list[str]:
    block = extract_block(country_block, r'\bowned_planets\s*=\s*\{')
    if not block:
        return []

    return re.findall(r'\b\d+\b', block)


def extract_planet_block(gamestate: str, planet_id: str) -> str | None:
    planet_section = extract_block(gamestate, r'\bplanet\s*=\s*\{')
    if not planet_section:
        return None

    return extract_block(
        planet_section,
        rf'\b{re.escape(planet_id)}\s*=\s*\{{'
    )


def normalize_internal_value(value: float | None) -> float | None:
    """Stellaris stocke certaines valeurs planétaires en échelle interne x100."""
    if value is None:
        return None

    return round(value / 100, 2)



def clean_stellaris_name(value: str | None, fallback: str) -> str:
    if not value:
        return fallback

    value = value.strip().strip('"')

    # Certaines saves stockent des clés de localisation ou des tokens internes.
    # On les garde, mais on évite les chaînes vides.
    if not value:
        return fallback

    return value


def extract_planet_name(block: str, planet_id: str) -> dict:
    """
    V2.3 — extraction de nom plus robuste.

    Stellaris peut stocker les noms sous plusieurs formes :
    - name="Earth"
    - name={ key="NAME_Earth" }
    - name={ name="Earth" }
    - custom_name="..."
    - sector/name variants selon versions/mods

    Si on ne trouve rien de lisible, on garde Planet <id>.
    """
    fallback = f"Planet {planet_id}"

    patterns = [
        r'\bcustom_name\s*=\s*"([^"]+)"',
        r'\bname\s*=\s*"([^"]+)"',
        r'\bname\s*=\s*\{[^{}]*?\bname\s*=\s*"([^"]+)"',
        r'\bname\s*=\s*\{[^{}]*?\bkey\s*=\s*"([^"]+)"',
        r'\bplanet_name\s*=\s*"([^"]+)"',
    ]

    raw_candidates = []

    for pattern in patterns:
        match = re.search(pattern, block, re.DOTALL)
        if match:
            raw_candidates.append(match.group(1))

    resolved = fallback
    raw = None
    source = "fallback"

    for candidate in raw_candidates:
        cleaned = clean_stellaris_name(candidate, fallback)
        raw = cleaned

        # Si c'est une clé de localisation générique, c'est mieux que rien,
        # mais on préfère un vrai nom lisible si on en trouve un autre.
        if not cleaned.startswith(("NAME_", "PRESCRIPTED_", "format.")):
            resolved = cleaned
            source = "direct"
            break

        if resolved == fallback:
            resolved = cleaned
            source = "localization_key"

    return {
        "name": resolved,
        "raw_name": raw,
        "name_source": source,
    }


def build_planet_advice(planet: dict) -> list[str]:
    advice = []

    specialization = planet.get("specialization_guess")
    stability = planet.get("stability")
    amenities = planet.get("free_amenities_normalized")
    housing = planet.get("free_housing_normalized")
    crime = planet.get("crime")

    if amenities is not None and amenities < -5:
        advice.append("Corriger en priorité les amenities : ajouter jobs/bâtiments qui produisent des amenities.")
    elif amenities is not None and amenities < -1:
        advice.append("Surveiller les amenities : le déficit commence à peser sur la stabilité.")

    if stability is not None and stability < 30:
        advice.append("Stabilité critique : traiter cette planète avant de poursuivre l’expansion.")
    elif stability is not None and stability < 40:
        advice.append("Stabilité basse : risque de perte d’efficacité et de troubles.")

    if crime is not None and crime >= 40:
        advice.append("Crime à surveiller : ajouter de l’enforcement ou corriger les causes de stabilité.")

    if housing is not None and housing < -1:
        advice.append("Housing négatif : ajouter districts/logements ou réduire la pression de population.")

    if specialization == "Forge World" and amenities is not None and amenities < -1:
        advice.append("Forge World sous pression : l’industrie lourde semble dépasser le support interne.")
    elif specialization == "Tech World" and amenities is not None and amenities < -1:
        advice.append("Tech World instable : sécuriser les amenities pour éviter de ralentir la recherche.")
    elif specialization == "Industrial World" and amenities is not None and amenities < -1:
        advice.append("Industrial World fragile : vérifier biens de consommation/amenities.")

    if not advice:
        advice.append("Aucune action prioritaire détectée.")

    return advice


def compute_planet_efficiency_score(planet: dict) -> int:
    """
    V2.3.1 — score toujours calculable.

    Certaines planètes Stellaris n'exposent pas toujours toutes les valeurs
    attendues selon leur type, leur état ou la version de save.

    Avant, si une valeur restait None dans certains chemins, le front pouvait
    afficher "?". Maintenant, les valeurs manquantes sont traitées comme neutres
    et on calcule aussi un data_completeness_score séparé.
    """
    score = 100

    stability = planet.get("stability")
    amenities = planet.get("free_amenities_normalized")
    housing = planet.get("free_housing_normalized")
    crime = planet.get("crime")

    if stability is None:
        stability = 50

    if amenities is None:
        amenities = 0

    if housing is None:
        housing = 0

    if crime is None:
        crime = 0

    if stability < 30:
        score -= 35
    elif stability < 40:
        score -= 25
    elif stability < 50:
        score -= 12

    if amenities < -5:
        score -= 25
    elif amenities < -2:
        score -= 15
    elif amenities < -1:
        score -= 8

    if housing < -1:
        score -= 10

    if crime >= 70:
        score -= 20
    elif crime >= 40:
        score -= 10

    return int(clamp(score))


def compute_planet_data_completeness(planet: dict) -> int:
    fields = [
        "stability",
        "crime",
        "free_housing_normalized",
        "free_amenities_normalized",
    ]

    found = sum(1 for field in fields if planet.get(field) is not None)

    return int(round((found / len(fields)) * 100))


def guess_planet_specialization(block: str) -> str:
    """
    Heuristique simple V1.5.1.
    On devine la spécialisation d'une planète à partir des jobs/productions
    présents dans son bloc de save.
    """
    patterns = {
        "Forge World": [
            "planet_metallurgists",
            "alloys",
        ],
        "Tech World": [
            "planet_researchers",
            "physics_research",
            "society_research",
            "engineering_research",
        ],
        "Generator World": [
            "planet_technician",
            "energy",
        ],
        "Mining World": [
            "planet_miners",
            "minerals",
        ],
        "Agri World": [
            "planet_farmers",
            "food",
        ],
        "Trade World": [
            "planet_traders",
            "trade",
        ],
        "Industrial World": [
            "planet_artisans",
            "consumer_goods",
        ],
        "Unity World": [
            "planet_bureaucrats",
            "planet_politicians",
            "unity",
        ],
        "Fortress World": [
            "planet_soldiers",
            "soldier",
            "naval_cap",
            "defense_armies",
        ],
    }

    scores = {}

    for specialization, keywords in patterns.items():
        score = 0

        for keyword in keywords:
            score += len(re.findall(rf'\b{re.escape(keyword)}\b', block))

        scores[specialization] = score

    best_name, best_score = max(scores.items(), key=lambda item: item[1])

    if best_score <= 0:
        return "Unknown"

    return best_name


def summarize_planet_specializations(planets: list[dict]) -> dict:
    summary = {}

    for planet in planets:
        specialization = planet.get("specialization_guess", "Unknown")
        summary[specialization] = summary.get(specialization, 0) + 1

    return dict(sorted(summary.items(), key=lambda item: (-item[1], item[0])))


def planet_problem_weight(planet: dict) -> tuple:
    stability = planet.get("stability")
    amenities = planet.get("free_amenities_normalized")
    crime = planet.get("crime")

    return (
        stability if stability is not None else 999,
        amenities if amenities is not None else 999,
        -(crime or 0),
    )


def score_stability_owned_planets(gamestate: str, country_block: str):
    warnings = []
    planets_report = []

    planet_ids = extract_owned_planet_ids(country_block)

    if not planet_ids:
        return 60, ["Impossible de trouver tes planètes : score stabilité fallback."], [], []

    score = 85

    for planet_id in planet_ids:
        block = extract_planet_block(gamestate, planet_id)

        if not block:
            continue

        stability = extract_number(block, "stability", None)
        crime = extract_number(block, "crime", None)
        housing_raw = extract_number(block, "free_housing", None)
        amenities_raw = extract_number(block, "free_amenities", None)

        housing = normalize_internal_value(housing_raw)
        amenities = normalize_internal_value(amenities_raw)

        name_info = extract_planet_name(block, planet_id)
        name = name_info["name"]

        specialization = guess_planet_specialization(block)

        planet_alerts = []
        severity_score = 0

        if stability is not None and stability < 40:
            penalty = 12 if stability < 30 else 8
            score -= penalty
            severity_score += penalty
            planet_alerts.append(f"stabilité basse ({round(stability, 2)})")

        if crime is not None and crime >= 70:
            score -= 8
            severity_score += 8
            planet_alerts.append(f"criminalité élevée ({round(crime, 2)})")
        elif crime is not None and crime >= 40:
            score -= 4
            severity_score += 4
            planet_alerts.append(f"criminalité à surveiller ({round(crime, 2)})")

        if housing is not None and housing < -1:
            score -= 4
            severity_score += 4
            planet_alerts.append(f"logements insuffisants ({housing})")

        if amenities is not None and amenities < -1:
            if amenities < -5:
                penalty = 6
                severity = "grave"
            elif amenities < -2:
                penalty = 4
                severity = "moyen"
            else:
                penalty = 2
                severity = "léger"

            score -= penalty
            severity_score += penalty
            planet_alerts.append(f"amenities insuffisantes ({amenities}) [{severity}]")

        planet_entry = {
            "id": planet_id,
            "name": name,
            "raw_name": name_info.get("raw_name"),
            "name_source": name_info.get("name_source"),
            "display_name": name if name != f"Planet {planet_id}" else f"Planet {planet_id}",
            "specialization_guess": specialization,
            "stability": round(stability, 3) if stability is not None else None,
            "crime": round(crime, 3) if crime is not None else None,
            "free_housing_raw": housing_raw,
            "free_housing_normalized": housing,
            "free_amenities_raw": amenities_raw,
            "free_amenities_normalized": amenities,
            "problem_score": severity_score,
            "alerts": planet_alerts,
        }

        planet_entry["efficiency_score"] = compute_planet_efficiency_score(planet_entry)
        planet_entry["data_completeness_score"] = compute_planet_data_completeness(planet_entry)
        planet_entry["advice"] = build_planet_advice(planet_entry)

        planets_report.append(planet_entry)

    bad_planets = [p for p in planets_report if p["alerts"]]
    bad_planets.sort(key=lambda p: (-p["problem_score"], planet_problem_weight(p)))

    if bad_planets:
        for planet in bad_planets[:8]:
            warnings.append(
                f"{planet['name']} : " + ", ".join(planet["alerts"])
            )
    else:
        warnings.append("Aucun problème majeur détecté sur tes planètes.")

    return clamp(score), warnings, planets_report, bad_planets[:5]



def build_strategic_analysis(
    scores: dict,
    metrics: dict,
    resources: dict,
    specialization_summary: dict,
    top_problem_planets: list[dict]
) -> dict:
    """
    V1.6 — couche d'analyse stratégique.
    Ce n'est pas une vérité absolue : ce sont des heuristiques lisibles
    basées sur les métriques déjà extraites de la save.
    """
    income = resources.get("income", {})
    stockpile = resources.get("stockpile", {})

    economy_score = scores.get("economy", 0)
    military_score = scores.get("military", 0)
    research_score = scores.get("research", 0)
    stability_score = scores.get("stability", 0)

    research_density = metrics.get("research", {}).get("research_density")
    empire_size = metrics.get("empire", {}).get("empire_size", 0)

    archetypes = []

    if income.get("trade", 0) >= 1000:
        archetypes.append("Trade")

    if income.get("alloys", 0) >= 60:
        archetypes.append("Industrial")

    if military_score >= 70:
        archetypes.append("Militarist")

    if research_score >= 75 or (research_density is not None and research_density >= 4):
        archetypes.append("Technocratic")

    if stability_score < 45:
        archetypes.append("Internally-Unstable")

    if not archetypes:
        archetypes.append("Balanced")

    empire_archetype = "-".join(archetypes) + " Empire"

    strengths = []
    weaknesses = []
    recommendations = []
    priority_actions = []

    # Forces
    if economy_score >= 85:
        strengths.append("Économie extrêmement puissante.")

    if income.get("energy", 0) >= 800:
        strengths.append("Production énergétique massive.")

    if income.get("trade", 0) >= 1000:
        strengths.append("Économie de trade très développée.")

    if income.get("alloys", 0) >= 70:
        strengths.append("Très bonne production industrielle d’alliages.")

    if military_score >= 70:
        strengths.append("Capacité militaire crédible.")

    # Faiblesses
    if research_density is not None and research_density < 1:
        weaknesses.append("Recherche très faible par rapport à la taille de l’empire.")
    elif research_density is not None and research_density < 2:
        weaknesses.append("Recherche un peu faible par rapport à la taille de l’empire.")

    forge_worlds = specialization_summary.get("Forge World", 0)
    tech_worlds = specialization_summary.get("Tech World", 0)
    generator_worlds = specialization_summary.get("Generator World", 0)
    industrial_worlds = specialization_summary.get("Industrial World", 0)

    if forge_worlds >= 3 and tech_worlds <= 1:
        weaknesses.append("Empire sur-spécialisé en Forge Worlds par rapport aux Tech Worlds.")

    if stability_score < 40:
        weaknesses.append("Stabilité interne faible sur plusieurs planètes.")

    if stockpile.get("alloys", 0) < 300 and income.get("alloys", 0) >= 60:
        weaknesses.append("Production d’alliages correcte, mais réserve stratégique trop basse.")

    if income.get("consumer_goods", 0) < resources.get("expenses", {}).get("consumer_goods", 0):
        weaknesses.append("Biens de consommation en déficit net.")

    # Recommandations
    if research_density is not None and research_density < 1:
        recommendations.append("Ajouter rapidement des laboratoires et des pops chercheurs.")
        priority_actions.append("Créer ou convertir au moins une planète en Tech World.")
    elif research_density is not None and research_density < 2:
        recommendations.append("Augmenter progressivement la production scientifique.")

    if forge_worlds >= 3 and tech_worlds <= 1:
        recommendations.append("Convertir une Forge World peu performante ou instable en Tech World.")

    if top_problem_planets:
        first = top_problem_planets[0]
        recommendations.append(
            f"Stabiliser en priorité {first.get('name')} : " + ", ".join(first.get("alerts", []))
        )
        priority_actions.append("Corriger les amenities négatives sur les planètes critiques.")

    if stockpile.get("alloys", 0) < 300 and income.get("alloys", 0) >= 60:
        recommendations.append("Laisser monter le stock d’alliages avant une guerre ou une grosse vague de construction.")
        priority_actions.append("Viser au moins 500–1000 alliages en réserve.")

    if income.get("consumer_goods", 0) < resources.get("expenses", {}).get("consumer_goods", 0):
        recommendations.append("Réduire le déficit de biens de consommation ou convertir une planète industrielle/artisanale.")

    if generator_worlds >= 2 and income.get("energy", 0) >= 800:
        recommendations.append("Ton énergie est très forte : tu peux convertir une partie de cet avantage en science ou en stabilité.")

    # Verdict court
    if economy_score >= 85 and research_score < 60:
        verdict = "Empire très riche, mais qui ne transforme pas assez sa puissance économique en avance scientifique."
    elif military_score >= 70 and stability_score < 45:
        verdict = "Empire militairement crédible, mais fragilisé par des tensions internes."
    else:
        verdict = "Empire globalement viable, avec quelques axes d’optimisation."

    return {
        "empire_archetype": empire_archetype,
        "verdict": verdict,
        "main_strengths": strengths,
        "main_weaknesses": weaknesses,
        "strategic_recommendations": recommendations,
        "priority_actions": priority_actions,
        "detected_structure": {
            "forge_worlds": forge_worlds,
            "tech_worlds": tech_worlds,
            "generator_worlds": generator_worlds,
            "industrial_worlds": industrial_worlds,
            "empire_size": empire_size,
            "research_density": research_density,
        }
    }


def risk_level(score: int) -> str:
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"


def build_risk_analysis(
    scores: dict,
    metrics: dict,
    resources: dict,
    meta_benchmarking: dict,
    top_problem_planets: list[dict],
    strategic_analysis: dict,
) -> dict:
    """
    V1.9 — Empire Risk Engine.
    Analyse heuristique des risques de collapse / sur-extension / retard tech / préparation de guerre.
    """
    income = resources.get("income", {})
    stockpile = resources.get("stockpile", {})
    expenses = resources.get("expenses", {})

    research_density = metrics.get("research", {}).get("research_density")
    empire_size = metrics.get("empire", {}).get("empire_size", 0)
    military_power = metrics.get("military", {}).get("military_power", 0)
    alloys_income = income.get("alloys", 0)
    alloys_stock = stockpile.get("alloys", 0)

    economy_score = scores.get("economy", 0)
    research_score = scores.get("research", 0)
    military_score = scores.get("military", 0)
    stability_score = scores.get("stability", 0)

    risk_points = {
        "internal_instability": 0,
        "scientific_delay": 0,
        "economic_overextension": 0,
        "war_readiness": 0,
        "strategic_reserve": 0,
    }

    risk_factors = []
    protective_factors = []
    recommendations = []

    # Instabilité interne
    if stability_score < 35:
        risk_points["internal_instability"] += 35
        risk_factors.append("Stabilité interne très basse.")
    elif stability_score < 55:
        risk_points["internal_instability"] += 20
        risk_factors.append("Stabilité interne fragile.")

    if len(top_problem_planets) >= 3:
        risk_points["internal_instability"] += 25
        risk_factors.append("Plusieurs planètes critiques détectées.")
    elif top_problem_planets:
        risk_points["internal_instability"] += 10
        risk_factors.append("Quelques planètes nécessitent une stabilisation.")

    # Retard scientifique
    research_curve = meta_benchmarking.get("research_curve")
    if research_curve == "Far Behind":
        risk_points["scientific_delay"] += 40
        risk_factors.append("Recherche très en retard par rapport au benchmark temporel.")
    elif research_curve == "Behind":
        risk_points["scientific_delay"] += 25
        risk_factors.append("Recherche en retard par rapport au benchmark temporel.")

    if research_density is not None and research_density < 1:
        risk_points["scientific_delay"] += 25
        risk_factors.append("Densité scientifique trop basse pour la taille de l’empire.")
    elif research_density is not None and research_density < 2:
        risk_points["scientific_delay"] += 10
        risk_factors.append("Densité scientifique moyenne/faible.")

    # Sur-extension économique / structurelle
    consumer_goods_net = income.get("consumer_goods", 0) - expenses.get("consumer_goods", 0)
    if consumer_goods_net < 0:
        risk_points["economic_overextension"] += 20
        risk_factors.append("Déficit net de biens de consommation.")

    if empire_size >= 350 and research_density is not None and research_density < 1:
        risk_points["economic_overextension"] += 25
        risk_factors.append("Empire très large avec science insuffisante.")

    if economy_score >= 85 and research_score < 60:
        risk_points["economic_overextension"] += 15
        risk_factors.append("Croissance économique plus rapide que le scaling scientifique.")

    # Préparation militaire / guerre
    military_curve = meta_benchmarking.get("military_curve")
    if military_curve in {"Ahead", "Far Ahead"}:
        protective_factors.append("Puissance militaire au-dessus de la courbe benchmark.")
    elif military_curve in {"Behind", "Far Behind"}:
        risk_points["war_readiness"] += 25
        risk_factors.append("Puissance militaire sous la courbe benchmark.")

    if military_power > 10000:
        protective_factors.append("Puissance militaire brute crédible.")

    if alloys_income >= 70:
        protective_factors.append("Production d’alliages solide.")
    else:
        risk_points["war_readiness"] += 10
        risk_factors.append("Production d’alliages limitée pour soutenir une guerre longue.")

    # Réserve stratégique
    if alloys_stock < 200:
        risk_points["strategic_reserve"] += 35
        risk_factors.append("Réserve d’alliages très basse.")
    elif alloys_stock < 500:
        risk_points["strategic_reserve"] += 20
        risk_factors.append("Réserve d’alliages insuffisante.")
    else:
        protective_factors.append("Réserve d’alliages confortable.")

    if income.get("energy", 0) >= 800:
        protective_factors.append("Grosse marge énergétique exploitable.")

    total_risk_score = min(100, round(
        risk_points["internal_instability"] * 0.30
        + risk_points["scientific_delay"] * 0.25
        + risk_points["economic_overextension"] * 0.20
        + risk_points["war_readiness"] * 0.10
        + risk_points["strategic_reserve"] * 0.15
    ))

    # Niveaux de risque par domaine
    domain_risks = {
        "internal_instability": risk_level(risk_points["internal_instability"]),
        "scientific_delay": risk_level(risk_points["scientific_delay"]),
        "economic_overextension": risk_level(risk_points["economic_overextension"]),
        "war_readiness_risk": risk_level(risk_points["war_readiness"]),
        "strategic_reserve_risk": risk_level(risk_points["strategic_reserve"]),
    }

    # Collapse risk : risque agrégé spécifique à l’implosion / stagnation.
    collapse_score = min(100, round(
        risk_points["internal_instability"] * 0.45
        + risk_points["economic_overextension"] * 0.25
        + risk_points["scientific_delay"] * 0.20
        + risk_points["strategic_reserve"] * 0.10
    ))

    if collapse_score >= 70:
        collapse_risk = "High"
    elif collapse_score >= 40:
        collapse_risk = "Medium"
    else:
        collapse_risk = "Low"

    # War readiness positif, pas risque.
    if military_score >= 70 and alloys_income >= 60 and alloys_stock >= 500:
        war_readiness = "Excellent"
    elif military_score >= 70 and alloys_income >= 60:
        war_readiness = "Good but low reserves"
    elif military_score >= 50:
        war_readiness = "Moderate"
    else:
        war_readiness = "Weak"

    if collapse_risk in {"Medium", "High"}:
        recommendations.append("Stabiliser les planètes critiques avant de poursuivre l’expansion.")

    if domain_risks["scientific_delay"] in {"Medium", "High", "Critical"}:
        recommendations.append("Réinvestir la puissance économique dans des laboratoires et des chercheurs.")

    if domain_risks["strategic_reserve_risk"] in {"Medium", "High", "Critical"}:
        recommendations.append("Monter la réserve d’alliages avant toute guerre majeure.")

    if consumer_goods_net < 0:
        recommendations.append("Corriger le déficit de biens de consommation pour éviter d’étouffer la croissance scientifique.")

    if not recommendations:
        recommendations.append("Aucun risque critique immédiat : continuer à surveiller recherche, stabilité et réserves.")

    # Verdict lisible
    if collapse_risk == "High":
        verdict = "Empire puissant mais instable : risque élevé de crise interne ou de stagnation si rien n’est corrigé."
    elif collapse_risk == "Medium":
        verdict = "Empire fort mais sous tension : la croissance dépasse la capacité interne à stabiliser et scaler la science."
    elif domain_risks["scientific_delay"] in {"High", "Critical"}:
        verdict = "Empire viable, mais le retard scientifique devient le risque stratégique principal."
    else:
        verdict = "Risque global contenu : l’empire semble structurellement maîtrisable."

    return {
        "overall_risk_score": total_risk_score,
        "collapse_risk": collapse_risk,
        "collapse_score": collapse_score,
        "war_readiness": war_readiness,
        "domain_risks": domain_risks,
        "risk_points": risk_points,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "recommendations": recommendations,
        "verdict": verdict,
        "detected_flags": {
            "economic_overextension": risk_points["economic_overextension"] >= 25,
            "scientific_delay": risk_points["scientific_delay"] >= 25,
            "internal_instability": risk_points["internal_instability"] >= 25,
            "low_alloy_reserve": risk_points["strategic_reserve"] >= 20,
            "consumer_goods_deficit": consumer_goods_net < 0,
        }
    }


def build_audit(save_path: Path, forced_country_id: str | None = None):
    gamestate = read_save(save_path)

    country_id = (
        forced_country_id
        or find_player_country_id(gamestate)
        or find_country_id_from_meta(save_path)
    )

    if not country_id:
        raise ValueError("Impossible d’identifier le pays joueur.")

    country_block = extract_country_block(gamestate, country_id)

    if not country_block:
        raise ValueError(f"Impossible d’extraire le bloc country {country_id}.")

    stockpile = extract_stockpile(country_block)
    income, expenses = extract_budget(country_block)

    empire_size = extract_number(country_block, "empire_size", 0)

    metrics = build_metrics(country_block, gamestate, stockpile, income, expenses)

    economy, economy_warnings = score_economy(stockpile, income)
    research, research_warnings = score_research(income, stockpile, empire_size)
    military, military_warnings = score_military(country_block, income, stockpile)
    expansion, expansion_warnings = score_expansion(country_block)
    stability, stability_warnings, planets_report, top_problem_planets = score_stability_owned_planets(
        gamestate,
        country_block
    )

    planet_specialization_summary = summarize_planet_specializations(planets_report)

    scores = {
        "economy": economy,
        "military": military,
        "research": research,
        "expansion": expansion,
        "stability": stability,
    }

    global_score = clamp(sum(scores.values()) / len(scores))

    resources = {
        "stockpile": stockpile,
        "income": income,
        "expenses": expenses,
    }

    meta_benchmarking = build_meta_benchmarking({
        "save": str(save_path),
        "metrics": metrics,
        "resources": resources,
    })

    strategic_analysis = build_strategic_analysis(
        scores={**scores, "global": global_score},
        metrics=metrics,
        resources=resources,
        specialization_summary=planet_specialization_summary,
        top_problem_planets=top_problem_planets,
    )

    risk_analysis = build_risk_analysis(
        scores={**scores, "global": global_score},
        metrics=metrics,
        resources=resources,
        meta_benchmarking=meta_benchmarking,
        top_problem_planets=top_problem_planets,
        strategic_analysis=strategic_analysis,
    )

    return {
        "save": str(save_path),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "version": "2.4.0",
        "player_country_id": country_id,
        "scores": {
            **scores,
            "global": global_score,
        },
        "metrics": metrics,
        "planets": planets_report,
        "top_problem_planets": top_problem_planets,
        "planet_specialization_summary": planet_specialization_summary,
        "strategic_analysis": strategic_analysis,
        "risk_analysis": risk_analysis,
        "meta_benchmarking": meta_benchmarking,
        "resources": resources,
        "warnings": {
            "economy": economy_warnings,
            "military": military_warnings,
            "research": research_warnings,
            "expansion": expansion_warnings,
            "stability": stability_warnings,
        }
    }


def generate_metric_table(metrics: dict) -> str:
    rows = ""

    def add_section(title: str):
        nonlocal rows
        rows += f'<tr><th colspan="2">{title}</th></tr>'

    def add_row(label: str, value):
        nonlocal rows
        rows += f"<tr><td>{label}</td><td>{value}</td></tr>"

    for section_name, section in metrics.items():
        add_section(section_name)
        for key, value in section.items():
            add_row(key, value)

    return f"<table>{rows}</table>"



def generate_planets_table(planets: list[dict]) -> str:
    if not planets:
        return "<p>Aucune planète extraite.</p>"

    rows = ""
    rows += "<tr><th>Planète</th><th>Spécialisation</th><th>Stabilité</th><th>Crime</th><th>Amenities</th><th>Housing</th><th>Alertes</th></tr>"

    sorted_planets = sorted(
        planets,
        key=lambda p: (-p.get("problem_score", 0), p.get("stability") if p.get("stability") is not None else 999)
    )

    for planet in sorted_planets:
        alerts = "<br>".join(planet.get("alerts", [])) or "—"
        rows += (
            "<tr>"
            f"<td>{planet.get('name')}</td>"
            f"<td>{planet.get('specialization_guess')}</td>"
            f"<td>{planet.get('stability')}</td>"
            f"<td>{planet.get('crime')}</td>"
            f"<td>{planet.get('free_amenities_normalized')}</td>"
            f"<td>{planet.get('free_housing_normalized')}</td>"
            f"<td>{alerts}</td>"
            "</tr>"
        )

    return f"<table>{rows}</table>"

def generate_specialization_summary_table(summary: dict) -> str:
    if not summary:
        return "<p>Aucune spécialisation détectée.</p>"

    rows = "<tr><th>Spécialisation estimée</th><th>Nombre de planètes</th></tr>"

    for specialization, count in summary.items():
        rows += f"<tr><td>{specialization}</td><td>{count}</td></tr>"

    return f"<table>{rows}</table>"



def generate_strategic_analysis_html(analysis: dict) -> str:
    if not analysis:
        return "<p>Aucune analyse stratégique générée.</p>"

    def list_items(items):
        if not items:
            return "<p>—</p>"
        return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"

    structure = analysis.get("detected_structure", {})
    structure_rows = "".join(
        f"<tr><td>{key}</td><td>{value}</td></tr>"
        for key, value in structure.items()
    )

    return f"""
    <p><strong>Archétype :</strong> {analysis.get('empire_archetype')}</p>
    <p><strong>Verdict :</strong> {analysis.get('verdict')}</p>

    <h3>Forces</h3>
    {list_items(analysis.get('main_strengths', []))}

    <h3>Faiblesses</h3>
    {list_items(analysis.get('main_weaknesses', []))}

    <h3>Recommandations</h3>
    {list_items(analysis.get('strategic_recommendations', []))}

    <h3>Priorités</h3>
    {list_items(analysis.get('priority_actions', []))}

    <h3>Structure détectée</h3>
    <table>{structure_rows}</table>
    """



def generate_meta_benchmarking_html(meta: dict) -> str:
    if not meta:
        return "<p>Aucun benchmark généré.</p>"

    if "error" in meta:
        return f"<p>{meta['error']}</p>"

    def table_from_dict(data: dict):
        rows = ""
        for key, value in data.items():
            rows += f"<tr><td>{key}</td><td>{value}</td></tr>"
        return f"<table>{rows}</table>"

    return f"""
    <p><strong>Année détectée :</strong> {meta.get('save_year')}</p>
    <p><strong>Benchmark utilisé :</strong> {meta.get('benchmark_reference_year')}</p>
    <p><strong>Position meta :</strong> {meta.get('overall_meta_position')}</p>

    <h3>Courbes</h3>
    <table>
        <tr><th>Domaine</th><th>Position</th><th>Ratio</th></tr>
        <tr><td>Économie</td><td>{meta.get('economy_curve')}</td><td>{meta.get('ratios', {}).get('economy_ratio')}</td></tr>
        <tr><td>Recherche</td><td>{meta.get('research_curve')}</td><td>{meta.get('ratios', {}).get('research_ratio')}</td></tr>
        <tr><td>Militaire</td><td>{meta.get('military_curve')}</td><td>{meta.get('ratios', {}).get('military_ratio')}</td></tr>
    </table>

    <h3>Valeurs réelles</h3>
    {table_from_dict(meta.get('actual_values', {}))}

    <h3>Benchmarks</h3>
    {table_from_dict(meta.get('benchmarks', {}))}

    <p><em>{meta.get('note', '')}</em></p>
    """


def generate_risk_analysis_html(risk: dict) -> str:
    if not risk:
        return "<p>Aucune analyse de risque générée.</p>"

    def list_items(items):
        if not items:
            return "<p>—</p>"
        return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"

    def table_from_dict(data: dict):
        if not data:
            return "<p>—</p>"
        rows = ""
        for key, value in data.items():
            rows += f"<tr><td>{key}</td><td>{value}</td></tr>"
        return f"<table>{rows}</table>"

    return f"""
    <p><strong>Verdict risque :</strong> {risk.get('verdict')}</p>
    <p><strong>Score de risque global :</strong> {risk.get('overall_risk_score')}/100</p>
    <p><strong>Collapse risk :</strong> {risk.get('collapse_risk')} ({risk.get('collapse_score')}/100)</p>
    <p><strong>War readiness :</strong> {risk.get('war_readiness')}</p>

    <h3>Risques par domaine</h3>
    {table_from_dict(risk.get('domain_risks', {}))}

    <h3>Flags détectés</h3>
    {table_from_dict(risk.get('detected_flags', {}))}

    <h3>Facteurs de risque</h3>
    {list_items(risk.get('risk_factors', []))}

    <h3>Facteurs protecteurs</h3>
    {list_items(risk.get('protective_factors', []))}

    <h3>Recommandations risque</h3>
    {list_items(risk.get('recommendations', []))}
    """


def generate_html(audit: dict):
    scores = audit["scores"]
    metric_table = generate_metric_table(audit["metrics"])
    planets_table = generate_planets_table(audit.get("planets", []))
    specialization_summary_table = generate_specialization_summary_table(
        audit.get("planet_specialization_summary", {})
    )
    strategic_analysis_html = generate_strategic_analysis_html(
        audit.get("strategic_analysis", {})
    )
    meta_benchmarking_html = generate_meta_benchmarking_html(
        audit.get("meta_benchmarking", {})
    )
    risk_analysis_html = generate_risk_analysis_html(
        audit.get("risk_analysis", {})
    )

    warnings_html = ""

    for category, items in audit["warnings"].items():
        warnings_html += f"<h3>{category.capitalize()}</h3>"
        if not items:
            warnings_html += "<p>Rien de critique détecté.</p>"
        else:
            warnings_html += "<ul>"
            for item in items:
                warnings_html += f"<li>{item}</li>"
            warnings_html += "</ul>"

    return f"""
<html>
<head>
<meta charset="utf-8">
<title>Stellaris Audit</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1000px;
    margin: auto;
    padding: 32px;
    line-height: 1.5;
}}
.card {{
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}}
.score {{
    font-size: 38px;
    font-weight: bold;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
td, th {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background: #f0f0f0;
}}
pre {{
    background: #f5f5f5;
    padding: 16px;
    border-radius: 12px;
    overflow: auto;
}}
</style>
</head>
<body>

<h1>Stellaris Empire Auditor — V2.4.0</h1>

<div class="card">
    <div class="score">Score global : {scores["global"]}/100</div>
</div>

<div class="card">
    <h2>Scores</h2>
    <ul>
        <li>Économie : {scores["economy"]}/100</li>
        <li>Militaire : {scores["military"]}/100</li>
        <li>Recherche : {scores["research"]}/100</li>
        <li>Expansion : {scores["expansion"]}/100</li>
        <li>Stabilité : {scores["stability"]}/100</li>
    </ul>
</div>

<div class="card">
    <h2>Analyse stratégique</h2>
    {strategic_analysis_html}
</div>

<div class="card">
    <h2>Meta benchmarking</h2>
    {meta_benchmarking_html}
</div>

<div class="card">
    <h2>Risk Engine</h2>
    {risk_analysis_html}
</div>

<div class="card">
    <h2>Métriques brutes</h2>
    {metric_table}
</div>

<div class="card">
    <h2>Résumé des spécialisations</h2>
    {specialization_summary_table}
</div>

<div class="card">
    <h2>Planètes</h2>
    {planets_table}
</div>

<div class="card">
    <h2>Alertes</h2>
    {warnings_html}
</div>

<div class="card">
    <h2>JSON complet</h2>
    <pre>{json.dumps(audit, indent=2, ensure_ascii=False)}</pre>
</div>

</body>
</html>
"""




def compute_growth(old_value, new_value):
    if old_value is None or old_value == 0:
        return None
    return round(((new_value - old_value) / old_value) * 100, 2)


def delta(old_value, new_value):
    if old_value is None or new_value is None:
        return None
    return round(new_value - old_value, 2)


def safe_get(data: dict, path: list, default=0):
    cursor = data
    for key in path:
        if not isinstance(cursor, dict):
            return default
        cursor = cursor.get(key, default)
    return cursor


def build_timeline_analysis(old_audit: dict, new_audit: dict) -> dict:
    old_income = old_audit["resources"].get("income", {})
    new_income = new_audit["resources"].get("income", {})

    old_stock = old_audit["resources"].get("stockpile", {})
    new_stock = new_audit["resources"].get("stockpile", {})

    old_scores = old_audit.get("scores", {})
    new_scores = new_audit.get("scores", {})

    old_metrics = old_audit.get("metrics", {})
    new_metrics = new_audit.get("metrics", {})

    old_economy_core = (
        old_income.get("energy", 0)
        + old_income.get("minerals", 0)
        + old_income.get("food", 0)
        + old_income.get("alloys", 0)
        + old_income.get("consumer_goods", 0)
    )

    new_economy_core = (
        new_income.get("energy", 0)
        + new_income.get("minerals", 0)
        + new_income.get("food", 0)
        + new_income.get("alloys", 0)
        + new_income.get("consumer_goods", 0)
    )

    old_research = safe_get(old_metrics, ["research", "research_total"], 0)
    new_research = safe_get(new_metrics, ["research", "research_total"], 0)

    old_research_density = safe_get(old_metrics, ["research", "research_density"], None)
    new_research_density = safe_get(new_metrics, ["research", "research_density"], None)

    old_military_power = safe_get(old_metrics, ["military", "military_power"], 0)
    new_military_power = safe_get(new_metrics, ["military", "military_power"], 0)

    old_empire_size = safe_get(old_metrics, ["empire", "empire_size"], 0)
    new_empire_size = safe_get(new_metrics, ["empire", "empire_size"], 0)

    old_alloys_income = old_income.get("alloys", 0)
    new_alloys_income = new_income.get("alloys", 0)

    old_alloys_stock = old_stock.get("alloys", 0)
    new_alloys_stock = new_stock.get("alloys", 0)

    old_energy_income = old_income.get("energy", 0)
    new_energy_income = new_income.get("energy", 0)

    old_trade_income = old_income.get("trade", 0)
    new_trade_income = new_income.get("trade", 0)

    growth = {
        "economy_core_growth_percent": compute_growth(old_economy_core, new_economy_core),
        "research_growth_percent": compute_growth(old_research, new_research),
        "military_power_growth_percent": compute_growth(old_military_power, new_military_power),
        "empire_size_growth_percent": compute_growth(old_empire_size, new_empire_size),
        "alloys_income_growth_percent": compute_growth(old_alloys_income, new_alloys_income),
        "alloys_stock_growth_percent": compute_growth(old_alloys_stock, new_alloys_stock),
        "energy_income_growth_percent": compute_growth(old_energy_income, new_energy_income),
        "trade_income_growth_percent": compute_growth(old_trade_income, new_trade_income),
    }

    score_delta = {
        "global": delta(old_scores.get("global"), new_scores.get("global")),
        "economy": delta(old_scores.get("economy"), new_scores.get("economy")),
        "military": delta(old_scores.get("military"), new_scores.get("military")),
        "research": delta(old_scores.get("research"), new_scores.get("research")),
        "expansion": delta(old_scores.get("expansion"), new_scores.get("expansion")),
        "stability": delta(old_scores.get("stability"), new_scores.get("stability")),
    }

    metric_delta = {
        "economy_core": delta(old_economy_core, new_economy_core),
        "research_total": delta(old_research, new_research),
        "research_density": delta(old_research_density, new_research_density),
        "military_power": delta(old_military_power, new_military_power),
        "empire_size": delta(old_empire_size, new_empire_size),
        "alloys_income": delta(old_alloys_income, new_alloys_income),
        "alloys_stock": delta(old_alloys_stock, new_alloys_stock),
        "energy_income": delta(old_energy_income, new_energy_income),
        "trade_income": delta(old_trade_income, new_trade_income),
    }

    strategic_shift = []
    recommendations = []

    economy_growth = growth["economy_core_growth_percent"]
    research_growth = growth["research_growth_percent"]
    military_growth = growth["military_power_growth_percent"]
    empire_growth = growth["empire_size_growth_percent"]
    stability_delta = score_delta["stability"]

    if economy_growth is not None and economy_growth > 25:
        strategic_shift.append("Croissance économique forte.")

    if military_growth is not None and military_growth > 40:
        strategic_shift.append("Militarisation rapide.")

    if empire_growth is not None and empire_growth > 20:
        strategic_shift.append("Expansion territoriale agressive.")

    if research_growth is not None and economy_growth is not None and research_growth < economy_growth:
        strategic_shift.append("La recherche scale plus lentement que l’économie.")
        recommendations.append("Réinvestir une partie de la croissance économique dans des laboratoires et des chercheurs.")

    if new_research_density is not None and old_research_density is not None and new_research_density < old_research_density:
        strategic_shift.append("La densité scientifique se dégrade.")
        recommendations.append("Limiter l’expansion ou augmenter fortement la recherche pour compenser l’empire size.")

    if stability_delta is not None and stability_delta < 0:
        strategic_shift.append("La stabilité interne se dégrade.")
        recommendations.append("Corriger les amenities et la stabilité des planètes critiques avant de poursuivre l’expansion.")

    if growth["alloys_stock_growth_percent"] is not None and growth["alloys_stock_growth_percent"] < 0:
        strategic_shift.append("La réserve d’alliages baisse.")
        recommendations.append("Laisser remonter le stock d’alliages avant une guerre ou une grosse vague de construction.")

    if not strategic_shift:
        strategic_shift.append("Évolution stable, aucun pivot stratégique majeur détecté.")

    if not recommendations:
        recommendations.append("Continuer à surveiller recherche, stabilité et stock d’alliages sur la prochaine save.")

    return {
        "old_save": old_audit.get("save"),
        "new_save": new_audit.get("save"),
        "old_generated_at": old_audit.get("generated_at"),
        "new_generated_at": new_audit.get("generated_at"),
        "growth": growth,
        "score_delta": score_delta,
        "metric_delta": metric_delta,
        "strategic_shift": strategic_shift,
        "recommendations": recommendations,
        "old_snapshot": {
            "scores": old_scores,
            "empire_archetype": safe_get(old_audit, ["strategic_analysis", "empire_archetype"], "Unknown"),
            "research_density": old_research_density,
            "empire_size": old_empire_size,
            "military_power": old_military_power,
            "meta_benchmarking": old_audit.get("meta_benchmarking", {}),
            "risk_analysis": old_audit.get("risk_analysis", {}),
        },
        "new_snapshot": {
            "scores": new_scores,
            "empire_archetype": safe_get(new_audit, ["strategic_analysis", "empire_archetype"], "Unknown"),
            "research_density": new_research_density,
            "empire_size": new_empire_size,
            "military_power": new_military_power,
            "meta_benchmarking": new_audit.get("meta_benchmarking", {}),
            "risk_analysis": new_audit.get("risk_analysis", {}),
        }
    }


def generate_timeline_html(report: dict) -> str:
    timeline = report["timeline_analysis"]
    old_audit = report["old_audit"]
    new_audit = report["new_audit"]

    def table_from_dict(data: dict):
        rows = ""
        for key, value in data.items():
            rows += f"<tr><td>{key}</td><td>{value}</td></tr>"
        return f"<table>{rows}</table>"

    shifts = "".join(f"<li>{item}</li>" for item in timeline["strategic_shift"])
    recommendations = "".join(f"<li>{item}</li>" for item in timeline["recommendations"])

    return f"""
<html>
<head>
<meta charset="utf-8">
<title>Stellaris Timeline Analysis</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1100px;
    margin: auto;
    padding: 32px;
    line-height: 1.5;
}}
.card {{
    border: 1px solid #ddd;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
td, th {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background: #f0f0f0;
}}
pre {{
    background: #f5f5f5;
    padding: 16px;
    border-radius: 12px;
    overflow: auto;
}}
.grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}}
</style>
</head>
<body>

<h1>Stellaris Empire Auditor — V1.9.0 Timeline</h1>

<div class="grid">
    <div class="card">
        <h2>Ancienne save</h2>
        <p><strong>Score global :</strong> {old_audit['scores']['global']}/100</p>
        <p><strong>Archétype :</strong> {old_audit.get('strategic_analysis', {}).get('empire_archetype', 'Unknown')}</p>
    </div>
    <div class="card">
        <h2>Nouvelle save</h2>
        <p><strong>Score global :</strong> {new_audit['scores']['global']}/100</p>
        <p><strong>Archétype :</strong> {new_audit.get('strategic_analysis', {}).get('empire_archetype', 'Unknown')}</p>
    </div>
</div>

<div class="card">
    <h2>Meta benchmarking — ancienne save</h2>
    {generate_meta_benchmarking_html(old_audit.get('meta_benchmarking', {}))}
</div>

<div class="card">
    <h2>Meta benchmarking — nouvelle save</h2>
    {generate_meta_benchmarking_html(new_audit.get('meta_benchmarking', {}))}
</div>

<div class="card">
    <h2>Risk Engine — ancienne save</h2>
    {generate_risk_analysis_html(old_audit.get('risk_analysis', {}))}
</div>

<div class="card">
    <h2>Risk Engine — nouvelle save</h2>
    {generate_risk_analysis_html(new_audit.get('risk_analysis', {}))}
</div>

<div class="card">
    <h2>Évolution des scores</h2>
    {table_from_dict(timeline['score_delta'])}
</div>

<div class="card">
    <h2>Croissance</h2>
    {table_from_dict(timeline['growth'])}
</div>

<div class="card">
    <h2>Delta métriques</h2>
    {table_from_dict(timeline['metric_delta'])}
</div>

<div class="card">
    <h2>Lecture stratégique</h2>
    <h3>Signaux détectés</h3>
    <ul>{shifts}</ul>
    <h3>Recommandations</h3>
    <ul>{recommendations}</ul>
</div>

<div class="card">
    <h2>JSON complet</h2>
    <pre>{json.dumps(report, indent=2, ensure_ascii=False)}</pre>
</div>

</body>
</html>
"""


def parse_cli_args(argv: list[str]):
    forced_country_id = None
    output_dir = Path("reports")
    positional = []

    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == "--country":
            if i + 1 >= len(argv):
                raise ValueError("Erreur : --country doit être suivi d’un ID.")
            forced_country_id = argv[i + 1]
            i += 2
            continue

        if arg == "--out":
            if i + 1 >= len(argv):
                raise ValueError("Erreur : --out doit être suivi d’un dossier.")
            output_dir = Path(argv[i + 1]).expanduser().resolve()
            i += 2
            continue

        if arg.startswith("--"):
            raise ValueError(f"Option inconnue : {arg}")

        positional.append(Path(arg).expanduser().resolve())
        i += 1

    return positional, forced_country_id, output_dir


def main():
    try:
        save_paths, forced_country_id, output_dir = parse_cli_args(sys.argv)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if len(save_paths) not in {1, 2}:
        print("Usage audit simple : python stellaris_auditor.py save.sav")
        print("Usage timeline    : python stellaris_auditor.py old.sav new.sav")
        print("Options           : --country 123 --out reports")
        sys.exit(1)

    for save_path in save_paths:
        if not save_path.exists():
            print(f"Fichier introuvable : {save_path}")
            sys.exit(1)

    output_dir.mkdir(exist_ok=True)

    if len(save_paths) == 1:
        save_path = save_paths[0]
        audit = build_audit(save_path, forced_country_id)

        base_name = save_path.stem.replace(" ", "_")
        json_path = output_dir / f"{base_name}_audit_v2_4_0.json"
        html_path = output_dir / f"{base_name}_audit_v2_4_0.html"

        json_path.write_text(
            json.dumps(audit, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        html_path.write_text(generate_html(audit), encoding="utf-8")

        print()
        print("Audit V2.4.0 généré :")
        print(json_path)
        print(html_path)
        print()
        print(f"Score global : {audit['scores']['global']}/100")
        return

    old_save, new_save = save_paths
    old_audit = build_audit(old_save, forced_country_id)
    new_audit = build_audit(new_save, forced_country_id)
    timeline = build_timeline_analysis(old_audit, new_audit)

    report = {
        "version": "2.4.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "old_audit": old_audit,
        "new_audit": new_audit,
        "timeline_analysis": timeline,
    }

    base_name = f"{old_save.stem.replace(' ', '_')}_to_{new_save.stem.replace(' ', '_')}"
    json_path = output_dir / f"{base_name}_timeline_v1_9_0.json"
    html_path = output_dir / f"{base_name}_timeline_v1_9_0.html"

    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    html_path.write_text(generate_timeline_html(report), encoding="utf-8")

    print()
    print("Timeline V1.9.0 générée :")
    print(json_path)
    print(html_path)
    print()
    print("Évolution score global :", timeline["score_delta"]["global"])


if __name__ == "__main__":
    main()
