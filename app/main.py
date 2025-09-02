import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.routes import router

# --- Konfigurasi Path & DEBUGGING ---
# Dapatkan direktori asas projek (root folder)
BASE_DIR = Path(__file__).resolve().parent.parent
# Tentukan path ke folder 'static'
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ===== PRINT STATEMENTS UNTUK DEBUGGING =====
print("--- DEBUGGING PATHS ---")
print(f"Current file (__file__): {__file__}")
print(f"BASE_DIR yang dikira: {BASE_DIR}")
print(f"STATIC_DIR yang dikira: {STATIC_DIR}")
print(f"Adakah STATIC_DIR wujud? {os.path.exists(STATIC_DIR)}")
if os.path.exists(STATIC_DIR):
    print(f"Kandungan dalam STATIC_DIR: {os.listdir(STATIC_DIR)}")
else:
    print("Folder STATIC_DIR tidak dijumpai di path tersebut.")
print("--- TAMAT DEBUGGING ---")
# ==========================================

# --- Cipta Aplikasi FastAPI ---
app = FastAPI()

# --- Sertakan API Routes ---
app.include_router(router)

# --- Mount Static Files ---
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
