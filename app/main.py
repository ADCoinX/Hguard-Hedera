from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.security.security_headers import SecurityHeadersMiddleware
from app.routes import router

app = FastAPI()

# Mount static files (for /static/Hguard-logo.png etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": str(exc)},
    )
