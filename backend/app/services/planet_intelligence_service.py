from .planet_enrichment_service import enrich_planets


def build_planet_intelligence_summary(planets: list[dict], pressure_summary: dict) -> str:
    if not planets:
        return "Aucune planète exploitable détectée."

    critical = pressure_summary.get("Critical", 0)
    high = pressure_summary.get("High", 0)

    forge_under_pressure = len([
        planet
        for planet in planets
        if planet.get("specialization_guess") == "Forge World"
        and planet.get("pressure_level") in ["Critical", "High"]
    ])

    if critical >= 2:
        return "Plusieurs planètes critiques : l’empire a un vrai problème de gestion interne."

    if forge_under_pressure >= 2:
        return "Les mondes industriels/forge concentrent la pression interne : l’économie lourde dépasse le support planétaire."

    if high >= 3:
        return "Plusieurs planètes sous forte pression : stabilisation recommandée avant nouvelle expansion."

    return "Pression planétaire globalement maîtrisable, avec quelques optimisations ciblées."


def build_planet_intelligence(audit: dict) -> dict:
    enrich_planets(audit)

    planets = [
        planet
        for planet in audit.get("planets", []) or []
        if isinstance(planet, dict)
    ]

    best_planets = sorted(
        planets,
        key=lambda planet: (
            planet.get("efficiency_score", 0),
            planet.get("stability") or 0,
            planet.get("data_completeness_score", 0),
        ),
        reverse=True,
    )[:5]

    worst_planets = sorted(
        planets,
        key=lambda planet: (
            planet.get("efficiency_score", 100),
            -(planet.get("problem_score", 0) or 0),
        ),
    )[:5]

    pressure_planets = sorted(
        [
            planet
            for planet in planets
            if planet.get("pressure_level") in ["Critical", "High"]
        ],
        key=lambda planet: (
            {
                "Critical": 0,
                "High": 1,
                "Medium": 2,
                "Low": 3,
            }.get(planet.get("pressure_level"), 9),
            -(planet.get("problem_score", 0) or 0),
        ),
    )[:8]

    specialization_issues = sorted(
        [
            planet
            for planet in planets
            if planet.get("specialization_issues")
        ],
        key=lambda planet: (
            len(planet.get("specialization_issues", [])),
            -(planet.get("problem_score", 0) or 0),
        ),
        reverse=True,
    )[:8]

    pressure_summary = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }

    for planet in planets:
        pressure_summary[planet.get("pressure_level", "Low")] = pressure_summary.get(
            planet.get("pressure_level", "Low"),
            0,
        ) + 1

    audit["planet_intelligence"] = {
        "best_planets": best_planets,
        "worst_planets": worst_planets,
        "pressure_planets": pressure_planets,
        "specialization_issues": specialization_issues,
        "pressure_summary": pressure_summary,
        "summary": build_planet_intelligence_summary(planets, pressure_summary),
    }

    return audit["planet_intelligence"]


def enrich_audit_planets(audit: dict) -> dict:
    build_planet_intelligence(audit)
    return audit
