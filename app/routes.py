import os
import re
import httpx
import time
import datetime
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from markupsafe import escape  # For HTML sanitization

# --- Konfigurasi ---
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)

APP_VERSION = "0.2.0"
HEDERA_MIRROR_NODE_API = "https://mainnet-public.mirrornode.hedera.com"
START_TIME = time.time()

# Regex untuk Hedera account ID (strict - no other chars allowed)
ACCOUNT_ID_RE = re.compile(r"^0\.0\.\d{1,20}$")

# Default setting untuk httpx
HTTPX_KW = dict(timeout=8.0, follow_redirects=False)

def is_valid_account(account_id: str) -> bool:
    """Strict validation for Hedera Account ID."""
    return bool(ACCOUNT_ID_RE.fullmatch(account_id or ""))

def sanitize_xml(s: str) -> str:
    """Basic XML escaping for user-controlled data."""
    # Hedera Account ID only allows digits and dot, but for extra safety:
    return escape(s)

# --- UI (Homepage) ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API: VALIDATE ---
@router.get("/validate")
async def validate_account(accountId: str):
    # Validate input (prevents user-controlled path construction)
    if not is_valid_account(accountId):
        raise HTTPException(status_code=400, detail="Invalid Account ID format. Example: 0.0.123")

    # All URLs below use validated accountId only
    acc_url = f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}"
    tx_url = f"{HEDERA_MIRROR_NODE_API}/api/v1/transactions"

    async with httpx.AsyncClient(**HTTPX_KW) as client:
        try:
            account_resp = await client.get(acc_url)
            account_resp.raise_for_status()
            account_data = account_resp.json() or {}

            tx_resp = await client.get(
                tx_url,
                params={"account.id": accountId, "limit": 100, "order": "desc"},
            )
            tx_resp.raise_for_status()
            tx_data = tx_resp.json() or {}

        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 404:
                # Escape output before reflecting to user
                raise HTTPException(status_code=404, detail=f"Account {escape(accountId)} not found.")
            raise HTTPException(status_code=502, detail="Mirror Node error")
        except Exception:
            raise HTTPException(status_code=500, detail="Unexpected error")

    balance_tinybar = (account_data.get("balance") or {}).get("balance") or 0
    transactions = tx_data.get("transactions") or []
    if not isinstance(transactions, list):
        transactions = []

    tx_count = len(transactions)
    last_5_tx = []
    for t in transactions[:5]:
        t = t or {}
        last_5_tx.append(
            {
                "transaction_id": escape(t.get("transaction_id", "")),  # sanitize for HTML/JSON
                "result": escape(t.get("result", "")),
                "consensus_timestamp": escape(t.get("consensus_timestamp", "")),
                "name": escape(t.get("name", "")),
            }
        )

    # Risk scoring
    score = 50
    flags = []
    try:
        if balance_tinybar > 1_000_000_000:
            score += 10
        if tx_count > 50:
            score += 15
        elif tx_count > 10:
            score += 5

        failed_tx_count = sum(1 for tx in transactions if (tx or {}).get("result") != "SUCCESS")
        if failed_tx_count > 0:
            score -= min(failed_tx_count * 5, 30)
            flags.append("HAS_FAILED_TX")

        if (account_data.get("key") or {}).get("_type") == "ProtobufEncoded":
            flags.append("COMPLEX_KEY")
            score += 5
    except Exception:
        flags.append("SCORE_FALLBACK")

    score = max(0, min(100, score))

    # All user-reflected data is escaped
    return {
        "accountId": escape(accountId),
        "balanceTinybar": int(balance_tinybar),
        "txCount": tx_count,
        "score": score,
        "last5Tx": last_5_tx,
        "flags": flags,
    }

# --- API: EXPORT ISO 20022 (pain.001) ---
@router.get("/export/iso20022/pain001")
async def export_iso(accountId: str):
    if not is_valid_account(accountId):
        raise HTTPException(status_code=400, detail="Invalid Account ID format. Example: 0.0.123")

    acc_url = f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}"

    async with httpx.AsyncClient(**HTTPX_KW) as client:
        try:
            account_resp = await client.get(acc_url)
            account_resp.raise_for_status()
            account_data = account_resp.json() or {}
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Account {escape(accountId)} not found.")
            raise HTTPException(status_code=502, detail="Mirror Node error")
        except Exception:
            raise HTTPException(status_code=500, detail="Unexpected error")

    balance_hbar = ((account_data.get("balance") or {}).get("balance") or 0) / 100_000_000

    # Escape user-controlled data for XML reflection (extra strict)
    safe_account_id = sanitize_xml(accountId)

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>HGUARD-RPT-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}</MsgId>
      <CreDtTm>{datetime.datetime.utcnow().isoformat()}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
      <DbtrAcct><Id><Othr><Id>{safe_account_id}</Id></Othr></Id></DbtrAcct>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="HBAR">{balance_hbar:.8f}</InstdAmt></Amt>
        <RmtInf><Ustrd>HGuard AML/CFT Report for Hedera Account {safe_account_id}</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>""".strip()

    return Response(
        content=xml_content,
        media_type="application/xml; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="HGuard-Report-{safe_account_id}.xml"'},
    )

# --- METRICS (Prometheus) ---
@router.get("/metrics")
async def get_metrics(request: Request):
    state = getattr(request.app, "state", None)
    metrics_data = getattr(state, "metrics", {}) if state else {}
    requests_total = int(metrics_data.get("requests_total", 0))
    lines = [
        "# HELP hguard_requests_total Total number of HTTP requests made to the application.",
        "# TYPE hguard_requests_total counter",
        f"hguard_requests_total {requests_total}",
    ]
    return Response(content="\n".join(lines), media_type="text/plain; version=0.0.4")

# --- VERSION ---
@router.get("/version")
async def get_version():
    return JSONResponse(
        {"version": APP_VERSION, "timestamp": datetime.datetime.utcnow().isoformat()}
    )

# --- HEALTH ---
@router.get("/health")
async def get_health():
    uptime = int(time.time() - START_TIME)
    return {"status": "ok", "uptime_seconds": uptime}
