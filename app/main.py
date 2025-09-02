from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.security.security_headers import SecurityHeadersMiddleware
from app.routes import router

# 1. Cipta aplikasi FastAPI
app = FastAPI()

# 2. Tambah middleware (diproses untuk setiap request)
app.add_middleware(SecurityHeadersMiddleware)

# 3. Sertakan semua route dari file lain
app.include_router(router)

# 4. Mount folder 'static' untuk akses CSS, imej, dll.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 5. Definisikan endpoint peringkat utama (seperti health check)
@app.get("/healthz")
async def healthz():
    return {"ok": True}

# 6. Definisikan handler untuk sebarang error yang tidak dijangka
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": str(exc)},
    )
