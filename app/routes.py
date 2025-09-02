from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import datetime

# --- Konfigurasi ---
router = APIRouter()
templates = Jinja2Templates(directory="templates")
APP_VERSION = "0.1.0-alpha"

# --- Route untuk UI (Homepage) ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Menyediakan laman utama (index.html)"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- Route untuk API yang diperlukan oleh JavaScript ---
@router.get("/validate")
async def validate_account(accountId: str):
    """
    API untuk validasi akaun.
    (Ini adalah contoh data, gantikan dengan logik sebenar anda)
    """
    if not accountId or not accountId.startswith("0.0."):
        raise HTTPException(status_code=400, detail="Invalid Account ID format.")
    
    # Data contoh untuk dipaparkan di frontend
    return {
        "accountId": accountId,
        "balanceTinybar": 123456789,
        "txCount": 42,
        "score": 85,
        "last5Tx": [
            {"transaction_id": "0.0.123-1620000000-000000000", "result": "SUCCESS"},
            {"transaction_id": "0.0.123-1610000000-000000000", "result": "SUCCESS"}
        ],
        "flags": ["KNOWN_EXCHANGE"]
    }

@router.get("/export/iso20022/pain001")
async def export_iso(accountId: str):
    """API untuk eksport data (contoh)."""
    content = f"Data ISO 20022 untuk akaun {accountId}"
    return HTMLResponse(content=content)

@router.get("/metrics")
async def get_metrics():
    """API untuk Prometheus metrics (contoh)."""
    return HTMLResponse(content="# FAKE METRICS\napp_requests_total 100\n")

@router.get("/version")
async def get_version():
    """API untuk memaparkan versi aplikasi."""
    return JSONResponse({"version": APP_VERSION, "timestamp": datetime.datetime.utcnow().isoformat()})
