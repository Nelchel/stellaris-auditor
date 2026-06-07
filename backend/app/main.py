from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import HealthResponse, AuditResponse
from .services import save_upload, run_single_audit, run_timeline_audit, list_reports, load_report, get_history_analytics

app = FastAPI(
    title="Stellaris Auditor API",
    version="3.5.0",
    description="FastAPI backend for Stellaris save analytics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "version": "3.5.0"}


@app.post("/audit", response_model=AuditResponse)
async def audit_save(save: UploadFile = File(...)):
    if not save.filename.endswith(".sav"):
        raise HTTPException(status_code=400, detail="File must be a .sav Stellaris save.")
    save_path = save_upload(save.file, save.filename, "single")
    data = run_single_audit(save_path)
    return {"mode": "single", "data": data}


@app.post("/compare", response_model=AuditResponse)
async def compare_saves(old_save: UploadFile = File(...), new_save: UploadFile = File(...)):
    if not old_save.filename.endswith(".sav") or not new_save.filename.endswith(".sav"):
        raise HTTPException(status_code=400, detail="Both files must be .sav Stellaris saves.")
    old_path = save_upload(old_save.file, old_save.filename, "old")
    new_path = save_upload(new_save.file, new_save.filename, "new")
    data = run_timeline_audit(old_path, new_path)
    return {"mode": "timeline", "data": data}


@app.get("/reports")
def reports():
    return {"reports": list_reports()}


@app.get("/reports/{filename}")
def report(filename: str):
    try:
        return load_report(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")


@app.get("/history")
def history():
    return get_history_analytics()
