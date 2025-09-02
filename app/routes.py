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
APP_VERSION = "0.1.0-alpha"
HEDERA_MIRROR_NODE_API = "https://mainnet-public.mirrornode.hedera.com"

# --- Route untuk UI (Homepage) ---
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API SEBENAR untuk VALIDATE ---
@router.get("/validate")
async def validate_account(accountId: str):
    """
    API untuk validasi akaun menggunakan data live dari Hedera Mirror Node.
    """
    if not accountId or not accountId.startswith("0.0."):
        raise HTTPException(status_code=400, detail="Invalid Account ID format.")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Dapatkan maklumat akaun (termasuk baki)
            account_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}")
            account_resp.raise_for_status() # Error jika akaun tak wujud (404)
            account_data = account_resp.json()

            # 2. Dapatkan transaksi (untuk kiraan dan 5 terakhir)
            tx_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/transactions?account.id={accountId}&limit=5&order=desc")
            tx_resp.raise_for_status()
            tx_data = tx_resp.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Account {accountId} not found.")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to fetch data from Hedera Mirror Node: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    # --- Proses data yang diterima ---
    balance_tinybar = account_data.get('balance', {}).get('balance', 0)
    
    # Kiraan transaksi tidak boleh didapati secara terus, kita guna anggaran atau data sedia ada
    # Untuk MVP, kita boleh tunjuk bilangan transaksi yang kita dapat (maksimum 5)
    tx_count = len(tx_data.get('transactions', [])) # Ini hanya tunjuk bilangan dalam page ini
    last_5_tx = tx_data.get('transactions', [])

    # --- Logik ringkas untuk skor risiko dan bendera ---
    score = 50  # Skor permulaan
    flags = []
    if balance_tinybar > 1_000_000_000: # Lebih 10 Hbar
        score += 10
    if len(last_5_tx) > 0:
        score += 10
    
    # Semak jika ada transaksi gagal
    if any(tx.get('result') != 'SUCCESS' for tx in last_5_tx):
        score -= 20
        flags.append("HAS_FAILED_TX")
    
    score = max(0, min(100, score)) # Pastikan skor antara 0-100

    # --- Hantar data sebenar ke frontend ---
    return {
        "accountId": accountId,
        "balanceTinybar": balance_tinybar,
        "txCount": tx_count, # Nota: Ini bukan jumlah keseluruhan, tapi kiraan dari API call
        "score": score,
        "last5Tx": last_5_tx,
        "flags": flags
    }

# --- API SEBENAR untuk EXPORT ISO 20022 (Contoh) ---
@router.get("/export/iso20022/pain001")
async def export_iso(accountId: str):
    """
    Menjana contoh file XML (bukan ISO 20022 sebenar) menggunakan data live.
    Ini adalah untuk tujuan demonstrasi sahaja.
    """
    # Dapatkan data akaun (sama seperti di atas)
    async with httpx.AsyncClient() as client:
        try:
            account_resp = await client.get(f"{HEDERA_MIRROR_NODE_API}/api/v1/accounts/{accountId}")
            account_resp.raise_for_status()
            account_data = account_resp.json()
        except Exception:
            return Response("Could not fetch account data to generate report.", media_type="text/plain", status_code=500)

    balance_hbar = account_data.get('balance', {}).get('balance', 0) / 100_000_000

    # Cipta kandungan XML ringkas
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
    <!-- This is a simplified example, NOT a valid pain.001 file. -->
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>MSG-{datetime.datetime.utcnow().isoformat()}</MsgId>
            <CreDtTm>{datetime.datetime.utcnow().isoformat()}</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
        </GrpHdr>
        <PmtInf>
            <Dbtr>
                <Nm>HGuard Report</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <Othr>
                        <Id>{accountId}</Id>
                    </Othr>
                </Id>
                <Ccy>HBAR</Ccy>
            </DbtrAcct>
            <CdtTrfTxInf>
                <Amt>
                    <InstdAmt Ccy="HBAR">{balance_hbar:.8f}</InstdAmt>
                </Amt>
                <RmtInf>
                    <Ustrd>Account balance report for {accountId}</Ustrd>
                </RmtInf>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""
    return Response(content=xml_content, media_type="application/xml", headers={
        "Content-Disposition": f"attachment; filename=report-{accountId}.xml"
    })

# --- Endpoint lain (kekal sama) ---
@router.get("/metrics")
async def get_metrics():
    return HTMLResponse(content="# FAKE METRICS\napp_requests_total 100\n")

@router.get("/version")
async def get_version():
    return JSONResponse({"version": APP_VERSION, "timestamp": datetime.datetime.utcnow().isoformat()})
