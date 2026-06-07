from pathlib import Path
from datetime import datetime
import shutil
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[2]
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
