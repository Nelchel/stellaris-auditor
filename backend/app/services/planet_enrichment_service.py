def _neutral_number(value, fallback):
    return fallback if value is None else value


def compute_planet_efficiency(planet: dict) -> int:
    score = 100

    stability = _neutral_number(planet.get("stability"), 50)
    amenities = _neutral_number(planet.get("free_amenities_normalized"), 0)
    housing = _neutral_number(planet.get("free_housing_normalized"), 0)
    crime = _neutral_number(planet.get("crime"), 0)

    try:
        stability = float(stability)
        amenities = float(amenities)
        housing = float(housing)
        crime = float(crime)
    except (TypeError, ValueError):
        return 50

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

    return max(0, min(100, int(round(score))))


def compute_planet_data_completeness(planet: dict) -> int:
    fields = [
        "stability",
        "crime",
        "free_housing_normalized",
        "free_amenities_normalized",
    ]

    found = sum(1 for field in fields if planet.get(field) is not None)

    return int(round((found / len(fields)) * 100))


def classify_planet_pressure(planet: dict) -> str:
    score = planet.get("problem_score", 0) or 0
    stability = planet.get("stability")
    amenities = planet.get("free_amenities_normalized")

    if stability is not None and stability < 30:
        return "Critical"

    if score >= 14:
        return "Critical"

    if amenities is not None and amenities < -5:
        return "High"

    if score >= 8:
        return "High"

    if score >= 3:
        return "Medium"

    return "Low"


def detect_specialization_issue(planet: dict) -> list[str]:
    issues = []

    spec = planet.get("specialization_guess", "Unknown")
    efficiency = planet.get("efficiency_score")
    stability = planet.get("stability")
    amenities = planet.get("free_amenities_normalized")
    crime = planet.get("crime")

    if efficiency is not None and efficiency < 60:
        issues.append("Efficacité faible pour sa spécialisation.")

    if spec == "Forge World":
        if amenities is not None and amenities < -1:
            issues.append("Forge World sous-supportée : amenities insuffisantes pour l’industrie lourde.")
        if stability is not None and stability < 40:
            issues.append("Forge World instable : risque de perte de rendement industriel.")

    if spec == "Tech World":
        if stability is not None and stability < 50:
            issues.append("Tech World instable : la recherche risque de souffrir.")
        if amenities is not None and amenities < -1:
            issues.append("Tech World avec déficit d’amenities : sécuriser le confort avant de stack les chercheurs.")

    if spec == "Industrial World" and amenities is not None and amenities < -1:
        issues.append("Industrial World fragile : vérifier amenities et biens de consommation.")

    if spec == "Generator World":
        if stability is not None and stability < 45:
            issues.append("Generator World sous tension : l’économie énergétique peut être moins efficace.")
        if amenities is not None and amenities < -5:
            issues.append("Generator World avec fort déficit d’amenities : support interne insuffisant.")

    if spec == "Unknown":
        if planet.get("data_completeness_score", 0) < 50:
            issues.append("Données insuffisantes : planète ou objet spécial mal identifié.")
        else:
            issues.append("Spécialisation non claire : probablement monde hybride ou parsing insuffisant.")

    if crime is not None and crime > 30:
        issues.append("Crime notable : peut devenir un problème si la stabilité baisse.")

    return issues


def estimate_planet_profitability(planet: dict) -> dict:
    efficiency = planet.get("efficiency_score", 50) or 50
    stability = planet.get("stability") or 50
    amenities = planet.get("free_amenities_normalized") or 0
    crime = planet.get("crime") or 0
    spec = planet.get("specialization_guess", "Unknown")

    profitability = efficiency

    if stability < 40:
        profitability -= 15

    if amenities < -5:
        profitability -= 20
    elif amenities < -2:
        profitability -= 10

    if crime > 25:
        profitability -= 10

    profitability = max(0, min(100, int(round(profitability))))

    economic_status = "Profitable"

    if profitability < 40:
        economic_status = "Economic Sink"
    elif profitability < 60:
        economic_status = "Underperforming"

    recommendations = []

    if spec == "Forge World" and amenities < -3:
        recommendations.append("Ajouter amenities/support avant de continuer l’industrialisation.")

    if spec == "Generator World" and efficiency < 70:
        recommendations.append("Cette planète pourrait être convertie vers une spécialisation industrielle ou hybride.")

    if spec == "Unknown":
        recommendations.append("Spécialisation incertaine : vérifier districts et bâtiments.")

    if stability < 35:
        recommendations.append("Stabiliser la planète avant tout investissement supplémentaire.")

    if profitability >= 85:
        recommendations.append("Planète très rentable : bon candidat pour scaling futur.")

    return {
        "profitability_score": profitability,
        "economic_status": economic_status,
        "economic_recommendations": recommendations,
    }


def enrich_planet(planet: dict) -> dict:
    if planet.get("efficiency_score") is None:
        planet["efficiency_score"] = compute_planet_efficiency(planet)

    planet["data_completeness_score"] = compute_planet_data_completeness(planet)
    planet["pressure_level"] = classify_planet_pressure(planet)
    planet["specialization_issues"] = detect_specialization_issue(planet)

    economic = estimate_planet_profitability(planet)
    planet["profitability_score"] = economic["profitability_score"]
    planet["economic_status"] = economic["economic_status"]
    planet["economic_recommendations"] = economic["economic_recommendations"]

    if not planet.get("display_name"):
        planet["display_name"] = planet.get("name") or f"Planet {planet.get('id', '?')}"

    return planet


def enrich_planets(audit: dict) -> dict:
    planets = audit.get("planets", []) or []
    by_id = {}

    for planet in planets:
        if isinstance(planet, dict):
            enrich_planet(planet)
            by_id[str(planet.get("id"))] = planet

    fixed_top = []

    for planet in audit.get("top_problem_planets", []) or []:
        if not isinstance(planet, dict):
            continue

        source = by_id.get(str(planet.get("id")))

        if source:
            planet.update(source)

        enrich_planet(planet)
        fixed_top.append(planet)

    if not fixed_top and planets:
        audit["top_problem_planets"] = sorted(
            [
                planet
                for planet in planets
                if planet.get("problem_score", 0) > 0 or planet.get("alerts")
            ],
            key=lambda planet: planet.get("problem_score", 0),
            reverse=True,
        )[:5]

    return audit
