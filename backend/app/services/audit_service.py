from pathlib import Path
from datetime import datetime

from app.stellaris_auditor_core import build_audit, build_timeline_analysis

from .report_service import save_report
from .planet_intelligence_service import enrich_audit_planets
from .evolution_service import build_evolution_analysis
from .narrative_service import build_campaign_narrative
from .visual_service import build_visual_analytics


def run_single_audit(save_path: Path) -> dict:
    audit = enrich_audit_planets(build_audit(save_path))
    save_report(audit, "single")
    return audit


def run_timeline_audit(old_save_path: Path, new_save_path: Path) -> dict:
    old_audit = enrich_audit_planets(build_audit(old_save_path))
    new_audit = enrich_audit_planets(build_audit(new_save_path))
    timeline = build_timeline_analysis(old_audit, new_audit)

    report = {
        "version": "3.5-api",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "old_audit": old_audit,
        "new_audit": new_audit,
        "timeline_analysis": timeline,
    }

    report["evolution_analysis"] = build_evolution_analysis(old_audit, new_audit)
    report["campaign_narrative"] = build_campaign_narrative(report)
    report["visual_analytics"] = build_visual_analytics(report)

    save_report(report, "timeline")

    return report
