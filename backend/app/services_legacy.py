from pathlib import Path
from datetime import datetime
import json
import shutil
from uuid import uuid4

from .stellaris_auditor_core import build_audit, build_timeline_analysis

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_obj, original_filename: str, prefix: str) -> Path:
    suffix = Path(original_filename).suffix or ".sav"
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prefix}_{uuid4().hex}{suffix}"
    path = UPLOAD_DIR / filename
    with path.open("wb") as buffer:
        shutil.copyfileobj(file_obj, buffer)
    return path


def save_report(data: dict, prefix: str) -> Path:
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prefix}_{uuid4().hex}.json"
    path = REPORT_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _neutral_number(value, fallback):
    return fallback if value is None else value


def compute_dashboard_efficiency(planet: dict) -> int:
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


def compute_dashboard_data_completeness(planet: dict) -> int:
    fields = ["stability", "crime", "free_housing_normalized", "free_amenities_normalized"]
    found = sum(1 for field in fields if planet.get(field) is not None)
    return int(round((found / len(fields)) * 100))


def ensure_planet_scores_for_audit(audit: dict) -> dict:
    planets = audit.get("planets", []) or []
    by_id = {}

    for planet in planets:
        if not isinstance(planet, dict):
            continue
        if planet.get("efficiency_score") is None:
            planet["efficiency_score"] = compute_dashboard_efficiency(planet)
        planet["data_completeness_score"] = compute_dashboard_data_completeness(planet)
        if not planet.get("display_name"):
            planet["display_name"] = planet.get("name") or f"Planet {planet.get('id', '?')}"
        by_id[str(planet.get("id"))] = planet

    fixed_top = []
    for planet in audit.get("top_problem_planets", []) or []:
        if not isinstance(planet, dict):
            continue
        source = by_id.get(str(planet.get("id")))
        if source:
            planet.update(source)
        if planet.get("efficiency_score") is None:
            planet["efficiency_score"] = compute_dashboard_efficiency(planet)
        planet["data_completeness_score"] = compute_dashboard_data_completeness(planet)
        if not planet.get("display_name"):
            planet["display_name"] = planet.get("name") or f"Planet {planet.get('id', '?')}"
        fixed_top.append(planet)

    if not fixed_top and planets:
        audit["top_problem_planets"] = sorted(
            [p for p in planets if p.get("problem_score", 0) > 0 or p.get("alerts")],
            key=lambda p: p.get("problem_score", 0),
            reverse=True,
        )[:5]

    return audit


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


def build_planet_intelligence_summary(planets: list[dict], pressure_summary: dict) -> str:
    if not planets:
        return "Aucune planète exploitable détectée."

    critical = pressure_summary.get("Critical", 0)
    high = pressure_summary.get("High", 0)
    forge_under_pressure = len([
        p for p in planets
        if p.get("specialization_guess") == "Forge World"
        and p.get("pressure_level") in ["Critical", "High"]
    ])

    if critical >= 2:
        return "Plusieurs planètes critiques : l’empire a un vrai problème de gestion interne."
    if forge_under_pressure >= 2:
        return "Les mondes industriels/forge concentrent la pression interne : l’économie lourde dépasse le support planétaire."
    if high >= 3:
        return "Plusieurs planètes sous forte pression : stabilisation recommandée avant nouvelle expansion."
    return "Pression planétaire globalement maîtrisable, avec quelques optimisations ciblées."


def build_planet_intelligence_for_audit(audit: dict) -> dict:
    planets = audit.get("planets", []) or []
    enriched = []

    for planet in planets:
        if not isinstance(planet, dict):
            continue

        if planet.get("efficiency_score") is None:
            planet["efficiency_score"] = compute_dashboard_efficiency(planet)

        planet["data_completeness_score"] = compute_dashboard_data_completeness(planet)
        planet["pressure_level"] = classify_planet_pressure(planet)
        planet["specialization_issues"] = detect_specialization_issue(planet)

        econ = estimate_planet_profitability(planet)
        planet["profitability_score"] = econ["profitability_score"]
        planet["economic_status"] = econ["economic_status"]
        planet["economic_recommendations"] = econ["economic_recommendations"]

        if not planet.get("display_name"):
            planet["display_name"] = planet.get("name") or f"Planet {planet.get('id', '?')}"

        enriched.append(planet)

    best_planets = sorted(
        enriched,
        key=lambda p: (p.get("efficiency_score", 0), p.get("stability") or 0, p.get("data_completeness_score", 0)),
        reverse=True,
    )[:5]

    worst_planets = sorted(
        enriched,
        key=lambda p: (p.get("efficiency_score", 100), -(p.get("problem_score", 0) or 0)),
    )[:5]

    pressure_planets = sorted(
        [p for p in enriched if p.get("pressure_level") in ["Critical", "High"]],
        key=lambda p: ({"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(p.get("pressure_level"), 9), -(p.get("problem_score", 0) or 0)),
    )[:8]

    specialization_issues = sorted(
        [p for p in enriched if p.get("specialization_issues")],
        key=lambda p: (len(p.get("specialization_issues", [])), -(p.get("problem_score", 0) or 0)),
        reverse=True,
    )[:8]

    pressure_summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for planet in enriched:
        pressure_summary[planet.get("pressure_level", "Low")] = pressure_summary.get(planet.get("pressure_level", "Low"), 0) + 1

    audit["planet_intelligence"] = {
        "best_planets": best_planets,
        "worst_planets": worst_planets,
        "pressure_planets": pressure_planets,
        "specialization_issues": specialization_issues,
        "pressure_summary": pressure_summary,
        "summary": build_planet_intelligence_summary(enriched, pressure_summary),
    }

    return audit["planet_intelligence"]


def ensure_planet_intelligence_for_audit(audit: dict) -> dict:
    ensure_planet_scores_for_audit(audit)
    build_planet_intelligence_for_audit(audit)
    return audit


def compare_scores(old_scores: dict, new_scores: dict) -> dict:
    deltas = {}
    for key in ["economy", "military", "research", "expansion", "stability", "global"]:
        old_val = old_scores.get(key, 0) or 0
        new_val = new_scores.get(key, 0) or 0
        deltas[key] = {"old": old_val, "new": new_val, "delta": round(new_val - old_val, 2)}
    return deltas


def compare_planets(old_audit: dict, new_audit: dict) -> dict:
    old_planets = {str(p.get("id")): p for p in old_audit.get("planets", []) if isinstance(p, dict)}
    new_planets = {str(p.get("id")): p for p in new_audit.get("planets", []) if isinstance(p, dict)}

    improved, worsened = [], []

    for pid, new_planet in new_planets.items():
        old_planet = old_planets.get(pid)
        if not old_planet:
            continue

        old_eff = old_planet.get("efficiency_score", 50) or 50
        new_eff = new_planet.get("efficiency_score", 50) or 50
        delta = round(new_eff - old_eff, 2)

        entry = {
            "id": pid,
            "name": new_planet.get("display_name") or new_planet.get("name"),
            "spec": new_planet.get("specialization_guess"),
            "old_efficiency": old_eff,
            "new_efficiency": new_eff,
            "delta": delta,
            "pressure": new_planet.get("pressure_level"),
        }

        if delta >= 8:
            improved.append(entry)
        if delta <= -8:
            worsened.append(entry)

    return {
        "improved": sorted(improved, key=lambda x: x["delta"], reverse=True)[:10],
        "worsened": sorted(worsened, key=lambda x: x["delta"])[:10],
    }


def build_evolution_analysis(old_audit: dict, new_audit: dict) -> dict:
    score_deltas = compare_scores(old_audit.get("scores", {}), new_audit.get("scores", {}))
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

    return {"score_deltas": score_deltas, "planet_changes": planets, "insights": insights}


def build_campaign_narrative(report: dict) -> dict:
    old_audit = report.get("old_audit", {})
    new_audit = report.get("new_audit", {})
    timeline = report.get("timeline_analysis", {})

    if not old_audit or not new_audit:
        return {}

    old_strat = old_audit.get("strategic_analysis", {})
    new_strat = new_audit.get("strategic_analysis", {})
    old_meta = old_audit.get("meta_benchmarking", {})
    new_meta = new_audit.get("meta_benchmarking", {})

    old_year = old_meta.get("save_year", "?")
    new_year = new_meta.get("save_year", "?")
    old_arch = old_strat.get("empire_archetype", "Unknown Empire")
    new_arch = new_strat.get("empire_archetype", "Unknown Empire")

    growth = timeline.get("growth", {})
    score_delta = timeline.get("score_delta", {})

    economy_growth = growth.get("economy_core_growth_percent")
    trade_growth = growth.get("trade_income_growth_percent")
    military_growth = growth.get("military_power_growth_percent")
    empire_growth = growth.get("empire_size_growth_percent")
    stability_delta = score_delta.get("stability", 0)
    economy_delta = score_delta.get("economy", 0)
    military_delta = score_delta.get("military", 0)

    old_density = old_audit.get("metrics", {}).get("research", {}).get("research_density")
    new_density = new_audit.get("metrics", {}).get("research", {}).get("research_density")

    narrative = [f"Entre {old_year} et {new_year}, l’empire est passé de « {old_arch} » à « {new_arch} »."]

    if economy_growth is not None and economy_growth > 80:
        narrative.append(f"La croissance économique a explosé (+{economy_growth}%), ce qui indique un vrai changement d’échelle.")
    elif economy_growth is not None and economy_growth > 25:
        narrative.append(f"L’économie progresse nettement (+{economy_growth}%), sans être totalement hors contrôle.")

    if military_growth is not None and military_growth > 150:
        narrative.append(f"La militarisation est massive (+{military_growth}% de puissance militaire), probablement alimentée par l’industrie et le trade.")
    elif military_growth is not None and military_growth > 50:
        narrative.append(f"La puissance militaire progresse fortement (+{military_growth}%).")

    if empire_growth is not None and empire_growth > 80:
        narrative.append(f"L’empire s’est énormément étendu (+{empire_growth}% d’empire size), ce qui augmente la pression administrative et scientifique.")

    if old_density is not None and new_density is not None and new_density < old_density:
        narrative.append(f"La densité scientifique se dégrade ({old_density} → {new_density}) : la science n’a pas suivi l’expansion.")

    if stability_delta < -20:
        narrative.append(f"La stabilité interne s’effondre ({stability_delta} points), signe que la croissance dépasse la capacité de gestion interne.")
    elif stability_delta < -5:
        narrative.append(f"La stabilité se dégrade ({stability_delta} points), à surveiller avant de continuer l’expansion.")

    turning_points = []
    if trade_growth is not None and trade_growth > 300:
        turning_points.append("Pivot majeur vers une économie de trade.")
    if military_growth is not None and military_growth > 150:
        turning_points.append("Militarisation rapide et changement de doctrine stratégique.")
    if empire_growth is not None and empire_growth > 80:
        turning_points.append("Expansion territoriale agressive.")
    if stability_delta < -20:
        turning_points.append("Dégradation brutale de la stabilité interne.")
    if old_arch != new_arch:
        turning_points.append(f"Changement d’archétype : {old_arch} → {new_arch}.")

    what_went_well = []
    if economy_delta > 10:
        what_went_well.append("La base économique a très fortement progressé.")
    if military_delta > 10:
        what_went_well.append("La puissance militaire est devenue crédible.")
    if new_meta.get("economy_curve") in ["Ahead", "Far Ahead"]:
        what_went_well.append("L’économie est au-dessus de la courbe benchmark.")
    if new_meta.get("military_curve") in ["Ahead", "Far Ahead"]:
        what_went_well.append("La puissance militaire est au-dessus de la courbe benchmark.")

    what_went_wrong = []
    if new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        what_went_wrong.append("La recherche décroche par rapport au rythme de développement.")
    if stability_delta < -10:
        what_went_wrong.append("La stabilité interne a été sacrifiée pendant la croissance.")
    flags = new_audit.get("risk_analysis", {}).get("detected_flags", {})
    if flags.get("consumer_goods_deficit"):
        what_went_wrong.append("Le déficit de biens de consommation risque de freiner le scaling scientifique.")
    if flags.get("low_alloy_reserve"):
        what_went_wrong.append("La réserve d’alliages est trop basse malgré une bonne production.")
    if flags.get("economic_overextension"):
        what_went_wrong.append("L’empire semble économiquement sur-étendu : trop large pour sa base scientifique/interne.")

    next_pivot = []
    if new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        next_pivot.append("Faire un pivot science : créer/convertir au moins une Tech World.")
    if new_audit.get("scores", {}).get("stability", 100) < 50:
        next_pivot.append("Stabiliser les planètes critiques avant nouvelle expansion.")
    if new_audit.get("resources", {}).get("stockpile", {}).get("alloys", 9999) < 500:
        next_pivot.append("Accumuler une réserve stratégique d’alliages avant guerre majeure.")
    if flags.get("consumer_goods_deficit"):
        next_pivot.append("Corriger les biens de consommation pour soutenir chercheurs et spécialistes.")
    if not next_pivot:
        next_pivot.append("Continuer le scaling, mais surveiller science et stabilité.")

    campaign_verdict = "Campagne en croissance forte."
    if stability_delta < -20 and new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        campaign_verdict = "Campagne très puissante mais dangereusement déséquilibrée : l’économie et la flotte progressent plus vite que la science et la stabilité."
    elif new_meta.get("economy_curve") in ["Ahead", "Far Ahead"] and new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        campaign_verdict = "Campagne économiquement dominante, mais technologiquement sous-scalée."
    elif new_audit.get("risk_analysis", {}).get("collapse_risk") == "Low":
        campaign_verdict = "Campagne saine : les risques restent contenus."

    return {
        "campaign_verdict": campaign_verdict,
        "main_trajectory": narrative,
        "turning_points": turning_points,
        "what_went_well": what_went_well,
        "what_went_wrong": what_went_wrong,
        "next_strategic_pivot": next_pivot,
        "summary": " ".join(narrative[:3]),
    }


def build_visual_analytics(report: dict) -> dict:
    old_audit = report.get("old_audit", {})
    new_audit = report.get("new_audit", {})
    timeline = report.get("timeline_analysis", {})

    if not old_audit or not new_audit:
        return {}

    old_year = old_audit.get("meta_benchmarking", {}).get("save_year", "old")
    new_year = new_audit.get("meta_benchmarking", {}).get("save_year", "new")
    labels = [str(old_year), str(new_year)]

    def score_series(key):
        return [old_audit.get("scores", {}).get(key, 0), new_audit.get("scores", {}).get(key, 0)]

    def metric(path, audit, fallback=0):
        cur = audit
        for part in path:
            if not isinstance(cur, dict):
                return fallback
            cur = cur.get(part, fallback)
        return cur if cur is not None else fallback

    income_old = old_audit.get("resources", {}).get("income", {})
    income_new = new_audit.get("resources", {}).get("income", {})

    economy_core_old = income_old.get("energy", 0) + income_old.get("minerals", 0) + income_old.get("alloys", 0)
    economy_core_new = income_new.get("energy", 0) + income_new.get("minerals", 0) + income_new.get("alloys", 0)

    old_specs = old_audit.get("planet_specialization_summary", {})
    new_specs = new_audit.get("planet_specialization_summary", {})
    spec_keys = sorted(set(old_specs.keys()) | set(new_specs.keys()))

    return {
        "labels": labels,
        "score_radar_old": [score_series("economy")[0], score_series("military")[0], score_series("research")[0], score_series("expansion")[0], score_series("stability")[0]],
        "score_radar_new": [score_series("economy")[1], score_series("military")[1], score_series("research")[1], score_series("expansion")[1], score_series("stability")[1]],
        "scores_over_time": {
            "global": score_series("global"),
            "economy": score_series("economy"),
            "military": score_series("military"),
            "research": score_series("research"),
            "stability": score_series("stability"),
        },
        "core_metrics": {
            "economy_core": [round(economy_core_old, 2), round(economy_core_new, 2)],
            "research_total": [round(metric(["metrics", "research", "research_total"], old_audit), 2), round(metric(["metrics", "research", "research_total"], new_audit), 2)],
            "military_power": [round(metric(["metrics", "military", "military_power"], old_audit), 2), round(metric(["metrics", "military", "military_power"], new_audit), 2)],
            "empire_size": [round(metric(["metrics", "empire", "empire_size"], old_audit), 2), round(metric(["metrics", "empire", "empire_size"], new_audit), 2)],
        },
        "risk_vs_stability": {
            "risk": [old_audit.get("risk_analysis", {}).get("overall_risk_score", 0), new_audit.get("risk_analysis", {}).get("overall_risk_score", 0)],
            "stability": [old_audit.get("scores", {}).get("stability", 0), new_audit.get("scores", {}).get("stability", 0)],
        },
        "research_pressure": {
            "research_density": [metric(["metrics", "research", "research_density"], old_audit), metric(["metrics", "research", "research_density"], new_audit)],
            "empire_size": [metric(["metrics", "empire", "empire_size"], old_audit), metric(["metrics", "empire", "empire_size"], new_audit)],
        },
        "specialization_shift": {
            "labels": spec_keys,
            "old": [old_specs.get(k, 0) for k in spec_keys],
            "new": [new_specs.get(k, 0) for k in spec_keys],
        },
        "planet_pressure": {
            "labels": list(new_audit.get("planet_intelligence", {}).get("pressure_summary", {}).keys()),
            "values": list(new_audit.get("planet_intelligence", {}).get("pressure_summary", {}).values()),
        },
        "growth": timeline.get("growth", {}),
        "score_delta": timeline.get("score_delta", {}),
        "metric_delta": timeline.get("metric_delta", {}),
    }


def enrich_single_audit(audit: dict) -> dict:
    ensure_planet_intelligence_for_audit(audit)
    return audit


def enrich_timeline_report(report: dict) -> dict:
    old_audit = enrich_single_audit(report["old_audit"])
    new_audit = enrich_single_audit(report["new_audit"])
    report["old_audit"] = old_audit
    report["new_audit"] = new_audit
    report["evolution_analysis"] = build_evolution_analysis(old_audit, new_audit)
    report["campaign_narrative"] = build_campaign_narrative(report)
    report["visual_analytics"] = build_visual_analytics(report)
    return report


def run_single_audit(save_path: Path) -> dict:
    audit = enrich_single_audit(build_audit(save_path))
    save_report(audit, "single")
    return audit


def run_timeline_audit(old_save_path: Path, new_save_path: Path) -> dict:
    old_audit = enrich_single_audit(build_audit(old_save_path))
    new_audit = enrich_single_audit(build_audit(new_save_path))
    timeline = build_timeline_analysis(old_audit, new_audit)

    report = {
        "version": "3.1-api",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "old_audit": old_audit,
        "new_audit": new_audit,
        "timeline_analysis": timeline,
    }

    report = enrich_timeline_report(report)
    save_report(report, "timeline")
    return report


def list_reports() -> list[dict]:
    reports = []
    for path in sorted(REPORT_DIR.glob("*.json"), reverse=True):
        reports.append({
            "filename": path.name,
            "created_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            "size": path.stat().st_size,
        })
    return reports


def load_report(filename: str) -> dict:
    path = REPORT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def extract_audits_from_report(report: dict) -> list[dict]:
    audits = []

    if "old_audit" in report:
        audits.append(report["old_audit"])

    if "new_audit" in report:
        audits.append(report["new_audit"])

    if "scores" in report and "metrics" in report:
        audits.append(report)

    return audits


def audit_identity(audit: dict) -> str:
    save = audit.get("save", "")
    year = audit.get("meta_benchmarking", {}).get("save_year")
    generated = audit.get("generated_at", "")
    return f"{save}|{year}|{generated}"


def load_history_audits() -> list[dict]:
    seen = set()
    audits = []

    for path in sorted(REPORT_DIR.glob("*.json")):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        for audit in extract_audits_from_report(report):
            ident = audit_identity(audit)

            if ident in seen:
                continue

            seen.add(ident)
            audit["_report_file"] = path.name
            audits.append(audit)

    def sort_key(audit: dict):
        year = audit.get("meta_benchmarking", {}).get("save_year")

        if year is None:
            return (0, audit.get("generated_at", ""))

        return (year, audit.get("generated_at", ""))

    return sorted(audits, key=sort_key)


def build_history_series(audits: list[dict]) -> dict:
    labels = []
    global_scores = []
    economy_scores = []
    military_scores = []
    research_scores = []
    stability_scores = []
    risk_scores = []

    research_totals = []
    research_density = []
    military_power = []
    economy_core = []
    empire_size = []

    archetypes = []

    for audit in audits:
        meta = audit.get("meta_benchmarking", {})
        year = meta.get("save_year")

        if year is None:
            year = len(labels)

        labels.append(str(year))

        scores = audit.get("scores", {})
        metrics = audit.get("metrics", {})
        income = audit.get("resources", {}).get("income", {})
        strategic = audit.get("strategic_analysis", {})
        risk = audit.get("risk_analysis", {})

        global_scores.append(scores.get("global", 0))
        economy_scores.append(scores.get("economy", 0))
        military_scores.append(scores.get("military", 0))
        research_scores.append(scores.get("research", 0))
        stability_scores.append(scores.get("stability", 0))
        risk_scores.append(risk.get("overall_risk_score", 0))

        research_totals.append(metrics.get("research", {}).get("research_total", 0))
        research_density.append(metrics.get("research", {}).get("research_density", 0))
        military_power.append(metrics.get("military", {}).get("military_power", 0))
        empire_size.append(metrics.get("empire", {}).get("empire_size", 0))

        core = (
            income.get("energy", 0)
            + income.get("minerals", 0)
            + income.get("alloys", 0)
        )

        economy_core.append(round(core, 2))
        archetypes.append(strategic.get("empire_archetype", "Unknown"))

    return {
        "labels": labels,
        "scores": {
            "global": global_scores,
            "economy": economy_scores,
            "military": military_scores,
            "research": research_scores,
            "stability": stability_scores,
            "risk": risk_scores,
        },
        "metrics": {
            "research_total": research_totals,
            "research_density": research_density,
            "military_power": military_power,
            "economy_core": economy_core,
            "empire_size": empire_size,
        },
        "archetypes": archetypes,
        "snapshots": [
            {
                "year": labels[index],
                "archetype": archetypes[index],
                "global": global_scores[index],
                "research": research_scores[index],
                "stability": stability_scores[index],
                "risk": risk_scores[index],
                "report_file": audits[index].get("_report_file", ""),
            }
            for index in range(len(audits))
        ],
    }


def get_history_analytics() -> dict:
    audits = load_history_audits()
    return {
        "count": len(audits),
        "audits": audits,
        "series": build_history_series(audits),
    }

