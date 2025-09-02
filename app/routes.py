import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import datetime

# --- Konfigurasi Path ---
# Dapatkan direktori asas projek (root folder)
BASE_DIR = Path(__file__).resolve().parent.parent
# Tentukan path ke folder 'templates'
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# --- Konfigurasi Router & Templates ---
router = APIRouter()
# Beritahu Jinja2 di mana nak cari file HTML
templates = Jinja2Templates(directory=TEMPLATE_DIR)
APP_VERSION = "0.1.0-alpha"

# --- Route untuk UI (Homepage) ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Menyediakan laman utama (index.html)"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- Route untuk API (kekal sama) ---
@router.get("/validate")
async def validate_account(accountId: str):
    if not accountId or not accountId.startswith("0.0."):
        raise HTTPException(status_code=400, detail="Invalid Account ID format.")
    return {
        "accountId": accountId, "balanceTinybar": 123456789, "txCount": 42, "score": 85,
        "last5Tx": [{"transaction_id": "0.0.123-1620000000-000000000", "result": "SUCCESS"}, {"transaction_id": "0.0.123-1610000000-000000000", "result": "SUCCESS"}],
        "flags": ["KNOWN_EXCHANGE"]
    }

@router.get("/export/iso20022/pain001")
async def export_iso(accountId: str):
    content = f"Data ISO 20022 untuk akaun {accountId}"
    return HTMLResponse(content=content)

@router.get("/metrics")
async def get_metrics():
    return HTMLResponse(content="# FAKE METRICS\napp_requests_total 100\n")

@router.get("/version")
async def get_version():
    return JSONResponse({"version": APP_VERSION, "timestamp": datetime.datetime.utcnow().isoformat()})
