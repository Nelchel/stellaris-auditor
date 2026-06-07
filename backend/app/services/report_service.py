from pathlib import Path
from datetime import datetime
import json
from uuid import uuid4

from .storage_service import REPORT_DIR


def save_report(data: dict, prefix: str) -> Path:
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prefix}_{uuid4().hex}.json"
    path = REPORT_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


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


def load_all_reports() -> list[tuple[Path, dict]]:
    reports = []

    for path in sorted(REPORT_DIR.glob("*.json")):
        try:
            reports.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue

    return reports
