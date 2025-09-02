import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
# from app.security.security_headers import SecurityHeadersMiddleware # Biarkan ia dikomen buat masa ini
from app.routes import router

# --- Konfigurasi Path ---
# Dapatkan direktori asas projek (root folder)
BASE_DIR = Path(__file__).resolve().parent.parent
# Tentukan path ke folder 'static'
STATIC_DIR = os.path.join(BASE_DIR, "static")

# --- Cipta Aplikasi FastAPI ---
app = FastAPI()

# --- Middleware (dibiarkan tidak aktif untuk ujian) ---
# app.add_middleware(SecurityHeadersMiddleware)

# --- Sertakan API Routes ---
app.include_router(router)

# --- Mount Static Files (dengan path yang tepat) ---
# Ini akan pastikan FastAPI tahu di mana nak cari /static/Hguard-logo.png
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Endpoint Utama ---
@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": str(exc)},
    )
