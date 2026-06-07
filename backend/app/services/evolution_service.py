def compare_scores(old_scores: dict, new_scores: dict) -> dict:
    deltas = {}

    for key in ["economy", "military", "research", "expansion", "stability", "global"]:
        old_value = old_scores.get(key, 0) or 0
        new_value = new_scores.get(key, 0) or 0

        deltas[key] = {
            "old": old_value,
            "new": new_value,
            "delta": round(new_value - old_value, 2),
        }

    return deltas


def compare_planets(old_audit: dict, new_audit: dict) -> dict:
    old_planets = {
        str(planet.get("id")): planet
        for planet in old_audit.get("planets", []) or []
        if isinstance(planet, dict)
    }

    new_planets = {
        str(planet.get("id")): planet
        for planet in new_audit.get("planets", []) or []
        if isinstance(planet, dict)
    }

    improved = []
    worsened = []

    for planet_id, new_planet in new_planets.items():
        old_planet = old_planets.get(planet_id)

        if not old_planet:
            continue

        old_efficiency = old_planet.get("efficiency_score", 50) or 50
        new_efficiency = new_planet.get("efficiency_score", 50) or 50
        delta = round(new_efficiency - old_efficiency, 2)

        entry = {
            "id": planet_id,
            "name": new_planet.get("display_name") or new_planet.get("name"),
            "spec": new_planet.get("specialization_guess"),
            "old_efficiency": old_efficiency,
            "new_efficiency": new_efficiency,
            "delta": delta,
            "pressure": new_planet.get("pressure_level"),
        }

        if delta >= 8:
            improved.append(entry)

        if delta <= -8:
            worsened.append(entry)

    return {
        "improved": sorted(improved, key=lambda item: item["delta"], reverse=True)[:10],
        "worsened": sorted(worsened, key=lambda item: item["delta"])[:10],
    }


def build_evolution_analysis(old_audit: dict, new_audit: dict) -> dict:
    score_deltas = compare_scores(
        old_audit.get("scores", {}),
        new_audit.get("scores", {}),
    )

    planets = compare_planets(old_audit, new_audit)
    insights = []

    if score_deltas["research"]["delta"] < 0:
        insights.append("La progression scientifique ralentit ou régresse.")

    if score_deltas["economy"]["delta"] > 5:
        insights.append("L’économie globale progresse correctement.")

    if score_deltas["stability"]["delta"] < -5:
        insights.append("La stabilité empire : expansion ou pression interne trop forte.")

    if score_deltas["military"]["delta"] > 5:
        insights.append("La puissance militaire augmente rapidement.")

    if not insights:
        insights.append("L’empire évolue de manière relativement stable.")

    return {
        "score_deltas": score_deltas,
        "planet_changes": planets,
        "insights": insights,
    }
