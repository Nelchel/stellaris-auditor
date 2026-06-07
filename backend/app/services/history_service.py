import re

from .report_service import load_all_reports


VALID_STELLARIS_YEAR_MIN = 2200
VALID_STELLARIS_YEAR_MAX = 3000


def extract_audits_from_report(report: dict) -> list[dict]:
    audits = []

    if "old_audit" in report:
        audits.append(report["old_audit"])

    if "new_audit" in report:
        audits.append(report["new_audit"])

    if "scores" in report and "metrics" in report:
        audits.append(report)

    return audits


def normalize_year(value) -> int | None:
    if value is None:
        return None

    try:
        year = int(float(value))
    except (TypeError, ValueError):
        return None

    if VALID_STELLARIS_YEAR_MIN <= year <= VALID_STELLARIS_YEAR_MAX:
        return year

    return None


def extract_year_from_text(value: str | None) -> int | None:
    if not value:
        return None

    text = str(value)

    # autosave_2285.01.01.sav / 2285.06.01 / save_2250.12.03
    matches = re.findall(r"(2[2-9]\d{2})\.\d{1,2}\.\d{1,2}", text)

    for match in matches:
        year = normalize_year(match)

        if year is not None:
            return year

    # fallback : parfois le nom contient juste 2285 sans date complète
    matches = re.findall(r"\b(2[2-9]\d{2})\b", text)

    for match in matches:
        year = normalize_year(match)

        if year is not None:
            return year

    return None


def get_audit_year(audit: dict) -> int | None:
    candidates = [
        audit.get("meta_benchmarking", {}).get("save_year"),
        audit.get("date"),
        audit.get("save_date"),
        audit.get("game_date"),
        audit.get("save"),
        audit.get("_report_file"),
    ]

    meta = audit.get("meta", {})

    if isinstance(meta, dict):
        candidates.extend([
            meta.get("date"),
            meta.get("name"),
        ])

    for candidate in candidates:
        year = normalize_year(candidate)

        if year is not None:
            return year

        year = extract_year_from_text(candidate)

        if year is not None:
            return year

    return None


def audit_identity(audit: dict, report_file: str, index: int) -> str:
    """
    Dédoublonnage souple.

    On ne jette plus les audits sans année. On évite juste les doublons exacts
    dans le même rapport et les doublons évidents de même save/scores.
    """
    save = str(audit.get("save", ""))
    year = get_audit_year(audit)
    scores = audit.get("scores", {})
    archetype = audit.get("strategic_analysis", {}).get("empire_archetype", "")

    if save:
        return "|".join([
            save,
            str(year),
            str(scores.get("global")),
            str(scores.get("economy")),
            str(scores.get("military")),
            str(scores.get("research")),
            str(scores.get("stability")),
            archetype,
        ])

    return "|".join([
        report_file,
        str(index),
        str(year),
        str(scores.get("global")),
        str(scores.get("research")),
        str(scores.get("stability")),
        archetype,
    ])


def load_history_audits() -> list[dict]:
    seen = set()
    audits = []

    for path, report in load_all_reports():
        extracted = extract_audits_from_report(report)

        for index, audit in enumerate(extracted):
            if not isinstance(audit, dict):
                continue

            year = get_audit_year(audit)
            identity = audit_identity(audit, path.name, index)

            if identity in seen:
                continue

            seen.add(identity)

            audit["_report_file"] = path.name
            audit["_history_year"] = year
            audit["_history_sort_key"] = (
                year if year is not None else 999999,
                path.stat().st_mtime,
                index,
            )

            audits.append(audit)

    return sorted(
        audits,
        key=lambda audit: audit.get("_history_sort_key", (999999, "", 0)),
    )


def display_label_for_audit(audit: dict, index: int) -> str:
    year = audit.get("_history_year")

    if year is not None:
        return str(year)

    return f"Snapshot {index + 1}"


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
    snapshots = []

    for index, audit in enumerate(audits):
        label = display_label_for_audit(audit, index)
        labels.append(label)

        scores = audit.get("scores", {})
        metrics = audit.get("metrics", {})
        income = audit.get("resources", {}).get("income", {})
        strategic = audit.get("strategic_analysis", {})
        risk = audit.get("risk_analysis", {})

        global_value = scores.get("global", 0)
        economy_value = scores.get("economy", 0)
        military_value = scores.get("military", 0)
        research_value = scores.get("research", 0)
        stability_value = scores.get("stability", 0)
        risk_value = risk.get("overall_risk_score", 0)

        global_scores.append(global_value)
        economy_scores.append(economy_value)
        military_scores.append(military_value)
        research_scores.append(research_value)
        stability_scores.append(stability_value)
        risk_scores.append(risk_value)

        research_totals.append(metrics.get("research", {}).get("research_total", 0))
        research_density.append(metrics.get("research", {}).get("research_density", 0))
        military_power.append(metrics.get("military", {}).get("military_power", 0))
        empire_size.append(metrics.get("empire", {}).get("empire_size", 0))

        core = income.get("energy", 0) + income.get("minerals", 0) + income.get("alloys", 0)
        economy_core.append(round(core, 2))

        archetype = strategic.get("empire_archetype", "Unknown")
        archetypes.append(archetype)

        snapshots.append({
            "year": label,
            "detected_year": audit.get("_history_year"),
            "archetype": archetype,
            "global": global_value,
            "research": research_value,
            "stability": stability_value,
            "risk": risk_value,
            "report_file": audit.get("_report_file", ""),
        })

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
        "snapshots": snapshots,
    }


def get_history_analytics() -> dict:
    audits = load_history_audits()

    return {
        "count": len(audits),
        "source": "local-backend",
        "audits": audits,
        "series": build_history_series(audits),
    }
