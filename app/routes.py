import re
from fastapi import APIRouter, Request, Response, Query
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
from app.api import hedera_client, scoring, iso_export
from app.db.session import engine
from app.models import ValidationLog
from app.utils.crypto import safe_hash
from sqlmodel import Session
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

router = APIRouter()

# Dummy build info
__version__ = "1.0.0"
__build_sha__ = os.getenv("BUILD_SHA", "dev")

@router.get("/validate")
async def validate(request: Request, accountId: str = Query(..., regex=r"^0\.0\.\d{1,20}$")):
    ip = request.client.host if request.client else "unknown"
    # Get account and last5Tx
    account, source_acc, latency_acc = await hedera_client.get_account(accountId)
    last5, source_tx, latency_tx = await hedera_client.get_last_txs(accountId, limit=5)
    if not account:
        return JSONResponse({"ok": False, "error": "Account not found"}, status_code=404)

    balance = int(account.get("balance", 0))
    tx_count = len(last5)
    score_val, flags = scoring.score(account, last5)
    # Log to DB
    with Session(engine) as sess:
        log = ValidationLog(
            account_hash=safe_hash(accountId),
            ip_hash=safe_hash(ip),
            score=score_val,
            source=source_acc or source_tx or "",
            latency_ms=int(latency_acc or latency_tx or 0)
        )
        sess.add(log)
        sess.commit()
    return {
        "accountId": accountId,
        "balanceTinybar": balance,
        "txCount": tx_count,
        "last5Tx": last5,
        "score": score_val,
        "flags": flags,
        "sourceUsed": source_acc or source_tx or "",
    }

@router.get("/export/iso20022/pain001")
async def export_iso(request: Request, accountId: str = Query(..., regex=r"^0\.0\.\d{1,20}$")):
    account, _, _ = await hedera_client.get_account(accountId)
    if not account:
        return JSONResponse({"ok": False, "error": "Account not found"}, status_code=404)
    balance = int(account.get("balance", 0))
    now_ts = request.headers.get("X-Now", "") or os.getenv("NOW_TS") or "2025-09-02"
    xml_str = iso_export.build_pain_001(accountId, balance, now_ts)
    return StreamingResponse(
        iter([xml_str]),
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{accountId}_pain001.xml"'}
    )

@router.get("/metrics")
async def metrics():
    # Dummy metric; extend with real stats as needed
    content = "# HELP validation_requests Total validation requests\n# TYPE validation_requests counter\nvalidation_requests 1\n"
    return PlainTextResponse(content, media_type="text/plain")

@router.get("/version")
async def version():
    return {"version": __version__, "build_sha": __build_sha__}
