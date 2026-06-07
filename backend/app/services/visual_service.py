def _metric(path: list[str], audit: dict, fallback=0):
    current = audit

    for part in path:
        if not isinstance(current, dict):
            return fallback

        current = current.get(part, fallback)

    return current if current is not None else fallback


def build_visual_analytics(report: dict) -> dict:
    old_audit = report.get("old_audit", {})
    new_audit = report.get("new_audit", {})
    timeline = report.get("timeline_analysis", {})

    if not old_audit or not new_audit:
        return {}

    old_year = old_audit.get("meta_benchmarking", {}).get("save_year", "old")
    new_year = new_audit.get("meta_benchmarking", {}).get("save_year", "new")
    labels = [str(old_year), str(new_year)]

    def score_series(key: str):
        return [
            old_audit.get("scores", {}).get(key, 0),
            new_audit.get("scores", {}).get(key, 0),
        ]

    income_old = old_audit.get("resources", {}).get("income", {})
    income_new = new_audit.get("resources", {}).get("income", {})

    economy_core_old = income_old.get("energy", 0) + income_old.get("minerals", 0) + income_old.get("alloys", 0)
    economy_core_new = income_new.get("energy", 0) + income_new.get("minerals", 0) + income_new.get("alloys", 0)

    old_specs = old_audit.get("planet_specialization_summary", {})
    new_specs = new_audit.get("planet_specialization_summary", {})
    spec_keys = sorted(set(old_specs.keys()) | set(new_specs.keys()))

    return {
        "labels": labels,
        "score_radar_old": [
            score_series("economy")[0],
            score_series("military")[0],
            score_series("research")[0],
            score_series("expansion")[0],
            score_series("stability")[0],
        ],
        "score_radar_new": [
            score_series("economy")[1],
            score_series("military")[1],
            score_series("research")[1],
            score_series("expansion")[1],
            score_series("stability")[1],
        ],
        "scores_over_time": {
            "global": score_series("global"),
            "economy": score_series("economy"),
            "military": score_series("military"),
            "research": score_series("research"),
            "stability": score_series("stability"),
        },
        "core_metrics": {
            "economy_core": [round(economy_core_old, 2), round(economy_core_new, 2)],
            "research_total": [
                round(_metric(["metrics", "research", "research_total"], old_audit), 2),
                round(_metric(["metrics", "research", "research_total"], new_audit), 2),
            ],
            "military_power": [
                round(_metric(["metrics", "military", "military_power"], old_audit), 2),
                round(_metric(["metrics", "military", "military_power"], new_audit), 2),
            ],
            "empire_size": [
                round(_metric(["metrics", "empire", "empire_size"], old_audit), 2),
                round(_metric(["metrics", "empire", "empire_size"], new_audit), 2),
            ],
        },
        "risk_vs_stability": {
            "risk": [
                old_audit.get("risk_analysis", {}).get("overall_risk_score", 0),
                new_audit.get("risk_analysis", {}).get("overall_risk_score", 0),
            ],
            "stability": [
                old_audit.get("scores", {}).get("stability", 0),
                new_audit.get("scores", {}).get("stability", 0),
            ],
        },
        "research_pressure": {
            "research_density": [
                _metric(["metrics", "research", "research_density"], old_audit),
                _metric(["metrics", "research", "research_density"], new_audit),
            ],
            "empire_size": [
                _metric(["metrics", "empire", "empire_size"], old_audit),
                _metric(["metrics", "empire", "empire_size"], new_audit),
            ],
        },
        "specialization_shift": {
            "labels": spec_keys,
            "old": [old_specs.get(key, 0) for key in spec_keys],
            "new": [new_specs.get(key, 0) for key in spec_keys],
        },
        "planet_pressure": {
            "labels": list(new_audit.get("planet_intelligence", {}).get("pressure_summary", {}).keys()),
            "values": list(new_audit.get("planet_intelligence", {}).get("pressure_summary", {}).values()),
        },
        "growth": timeline.get("growth", {}),
        "score_delta": timeline.get("score_delta", {}),
        "metric_delta": timeline.get("metric_delta", {}),
    }
