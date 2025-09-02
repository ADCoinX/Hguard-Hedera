import httpx
import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# --- Konfigurasi ---
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)
APP_VERSION = "0.2.0" # Naikkan versi
HEDERA_MIRROR_NODE_API = "https://mainnet-public.mirrornode.hedera.com"

# --- Route untuk UI (Homepage) ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API VALIDATE (DIBAIKI) ---
@router.get("/validate")
async def validate_account(accountId: str):
    if not accountId or not accountId.startswith("0.0."):
        raise HTTPException(status_code=400, detail="Invalid Account ID format.")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Dapatkan maklumat akaun
            account_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}")
            account_resp.raise_for_status()
            account_data = account_resp.json()

            # 2. Dapatkan 100 transaksi terakhir untuk kiraan yang betul
            tx_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/transactions?account.id={accountId}&limit=100&order=desc")
            tx_resp.raise_for_status()
            tx_data = tx_resp.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Account {accountId} not found.")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to fetch data from Hedera Mirror Node: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    # --- Proses data dengan logik yang lebih baik ---
    balance_tinybar = account_data.get('balance', {}).get('balance', 0)
    transactions = tx_data.get('transactions', [])
    
    # txCount kini betul (sehingga 100)
    tx_count = len(transactions)
    # last_5_tx adalah 5 yang pertama dari senarai
    last_5_tx = transactions[:5]

    # --- Logik skor risiko yang lebih baik ---
    score = 50
    flags = []
    if balance_tinybar > 100_000_000 * 10: score += 10 # Lebih 10 HBAR
    if tx_count > 50: score += 15 # Lebih aktif
    elif tx_count > 10: score += 5
    
    failed_tx_count = sum(1 for tx in transactions if tx.get('result') != 'SUCCESS')
    if failed_tx_count > 0:
        score -= failed_tx_count * 5 # Tolak 5 mata untuk setiap tx gagal
        flags.append("HAS_FAILED_TX")
    
    if account_data.get('key', {}).get('_type') == 'ProtobufEncoded':
        flags.append("COMPLEX_KEY")
        score += 5

    score = max(0, min(100, score)) # Pastikan skor antara 0-100

    return {
        "accountId": accountId,
        "balanceTinybar": balance_tinybar,
        "txCount": tx_count,
        "score": score,
        "last5Tx": last_5_tx,
        "flags": flags
    }

# --- API EXPORT ISO (KEKAL SAMA, SUDAH BETUL) ---
@router.get("/export/iso20022/pain001")
async def export_iso(accountId: str):
    # Dapatkan data akaun
    async with httpx.AsyncClient() as client:
        try:
            account_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}")
            account_resp.raise_for_status()
            account_data = account_resp.json()
        except Exception:
            return Response("Could not fetch account data to generate report.", media_type="text/plain", status_code=500)

    balance_hbar = account_data.get('balance', {}).get('balance', 0) / 100_000_000

    # Cipta kandungan XML
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>HGUARD-RPT-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}</MsgId>
            <CreDtTm>{datetime.datetime.utcnow().isoformat()}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
        </GrpHdr>
        <PmtInf>
            <DbtrAcct>
                <Id><Othr><Id>{accountId}</Id></Othr></Id>
            </DbtrAcct>
            <CdtTrfTxInf>
                <Amt><InstdAmt Ccy="HBAR">{balance_hbar:.8f}</InstdAmt></Amt>
                <RmtInf><Ustrd>HGuard AML/CFT Report for Hedera Account {accountId}</Ustrd></RmtInf>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>"""
    
    return Response(content=xml_content, media_type="application/xml", headers={
        "Content-Disposition": f"attachment; filename=HGuard-Report-{accountId}.xml"
    })

# --- METRIK LIVE (DIBAIKI) ---
@router.get("/metrics")
async def get_metrics(request: Request):
    """
    Menyediakan metrik LIVE dalam format Prometheus.
    """
    metrics_data = request.app.state.metrics
    requests_total = metrics_data.get("requests_total", 0)

    prometheus_output = [
        '# HELP hguard_requests_total Total number of HTTP requests made to the application.',
        '# TYPE hguard_requests_total counter',
        f'hguard_requests_total {requests_total}'
    ]
    
    return Response(content="\n".join(prometheus_output), media_type="text/plain")

# --- VERSION (KEKAL SAMA) ---
@router.get("/version")
async def get_version():
    return JSONResponse({"version": APP_VERSION, "timestamp": datetime.datetime.utcnow().isoformat()})
