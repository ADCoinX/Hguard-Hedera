import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.routes import router

# --- Konfigurasi Path ---
# Ini menentukan di mana letaknya folder 'static'
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "static")

# --- Cipta Aplikasi FastAPI ---
app = FastAPI(title="HGuard API")

# --- METRIK LIVE ---
# 1. Wujudkan 'state' untuk simpan kaunter
app.state.metrics = {
    "requests_total": 0
}

# 2. Wujudkan 'middleware' yang akan berjalan untuk setiap request
@app.middleware("http")
async def count_requests_middleware(request: Request, call_next):
    # Tambah 1 pada kaunter setiap kali ada request masuk
    request.app.state.metrics["requests_total"] += 1
    # Teruskan proses request seperti biasa
    response = await call_next(request)
    return response
# --------------------

# --- Sertakan API Routes ---
# Ini memuatkan semua endpoint dari app/routes.py (seperti /validate, /metrics, dll.)
app.include_router(router)

# --- Sediakan File Statik ---
# Ini memberitahu FastAPI cara untuk serve file CSS dan logo
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Endpoint Kesihatan (Health Check) ---
# Berguna untuk servis seperti Render tahu aplikasi sedang berjalan
@app.get("/healthz")
async def healthz():
    return {"ok": True}
