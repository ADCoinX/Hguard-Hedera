from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.security.security_headers import SecurityHeadersMiddleware

app = FastAPI()

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