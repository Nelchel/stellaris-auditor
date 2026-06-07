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

    # Exemples :
    # autosave_2285.01.01.sav
    # 2285.06.01
    # save_2250.12.03
    matches = re.findall(r"(2[2-9]\d{2})\.\d{1,2}\.\d{1,2}", str(value))

    for match in matches:
        year = normalize_year(match)
        if year is not None:
            return year

    return None


def get_audit_year(audit: dict) -> int | None:
    # 1. source préférée : meta_benchmarking.save_year, mais seulement si plausible.
    year = normalize_year(audit.get("meta_benchmarking", {}).get("save_year"))
    if year is not None:
        return year

    # 2. champs date éventuels.
    for key in ["date", "save_date", "game_date"]:
        year = extract_year_from_text(audit.get(key))
        if year is not None:
            return year

    # 3. chemin de la save.
    year = extract_year_from_text(audit.get("save"))
    if year is not None:
        return year

    # 4. meta brute éventuelle.
    meta = audit.get("meta", {})
    if isinstance(meta, dict):
        for key in ["date", "name"]:
            year = extract_year_from_text(meta.get(key))
            if year is not None:
                return year

    return None


def audit_identity(audit: dict) -> str:
    """
    Dédoublonnage plus stable.

    Avant, on incluait generated_at, ce qui créait des doublons quand la même
    save était auditée plusieurs fois. Maintenant on identifie surtout par :
    - chemin/nom de save
    - année Stellaris
    - scores clés
    - archétype
    """
    save = str(audit.get("save", ""))
    year = get_audit_year(audit)
    scores = audit.get("scores", {})
    archetype = audit.get("strategic_analysis", {}).get("empire_archetype", "")

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


def load_history_audits() -> list[dict]:
    seen = set()
    audits = []

    for path, report in load_all_reports():
        for audit in extract_audits_from_report(report):
            year = get_audit_year(audit)

            # On ignore les snapshots sans année Stellaris exploitable pour éviter
            # les lignes absurdes 0 / 1 / 9416.
            if year is None:
                continue

            identity = audit_identity(audit)

            if identity in seen:
                continue

            seen.add(identity)
            audit["_report_file"] = path.name
            audit["_history_year"] = year
            audits.append(audit)

    return sorted(
        audits,
        key=lambda audit: (
            audit.get("_history_year", 0),
            audit.get("generated_at", ""),
            audit.get("_report_file", ""),
        ),
    )


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
        year = audit.get("_history_year") or get_audit_year(audit)

        if year is None:
            continue

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

        core = income.get("energy", 0) + income.get("minerals", 0) + income.get("alloys", 0)
        economy_core.append(round(core, 2))
        archetypes.append(strategic.get("empire_archetype", "Unknown"))

    snapshots = []

    for index, audit in enumerate(audits[:len(labels)]):
        snapshots.append({
            "year": labels[index],
            "archetype": archetypes[index],
            "global": global_scores[index],
            "research": research_scores[index],
            "stability": stability_scores[index],
            "risk": risk_scores[index],
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
        "audits": audits,
        "series": build_history_series(audits),
    }
