📖 README.md (HGuard – Hedera Wallet Validator)

# HGuard – Hedera Wallet Validator 🔒

**HGuard** is a minimal viable product (MVP) built on the **Hedera Hashgraph** network.  
It provides **wallet validation**, **risk scoring**, and **ISO 20022 XML export** for compliance and audit use cases.

Developed by [ADCX Lab](https://autodigitalcoin.com).

---

## ✨ Features
- ✅ Validate Hedera Account IDs (`0.0.xxxx`) directly against Mirror Node API  
- ✅ Risk scoring (balance, transaction count, failed transaction ratio, anomaly detection)  
- ✅ Export **ISO 20022 (pain.001)** XML reports for compliance / AML/CFT monitoring  
- ✅ Live Prometheus metrics endpoint  
- ✅ Hardened security headers + SonarQube compliant fixes  

---

## 🏗️ Tech Stack
- [FastAPI](https://fastapi.tiangolo.com/) (Python backend)  
- [httpx](https://www.python-httpx.org/) (async API calls)  
- [Jinja2](https://jinja.palletsprojects.com/) (templating)  
- [Hedera Mirror Node API](https://docs.hedera.com/hedera/)  

---

## 🚀 Quick Start

### Clone Repo
```bash
git clone https://github.com/ADCoinX/Hguard-Hedera.git
cd Hguard-Hedera

Setup Environment

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Run Locally

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

👉 UI available at: http://localhost:8000

⸻

⚙️ Environment Variables

APP_ENV=production
LOG_LEVEL=info
LOG_SALT=your_secret_salt
PRIMARY_MIRROR_BASE=https://mainnet-public.mirrornode.hedera.com
CB_FAILURE_THRESHOLD=5
CB_RESET_SECONDS=30
RATE_LIMIT_RPS=10
ML_ENABLED=false


⸻

📡 API Endpoints

Endpoint	Description
/	UI Homepage
/validate?accountId=0.0.xxxx	Validate Hedera wallet
/export/iso20022/pain001?accountId=0.0.xxxx	Export ISO 20022 XML
/metrics	Prometheus metrics
/version	API version & timestamp


⸻

🛡️ Security & InfoSec

HGuard was designed to be lightweight, stateless, and secure:
	•	No private keys / seeds / PII stored – only public blockchain data is processed
	•	TLS 1.3 + HSTS enforced at deployment (Render/HTTPS)
	•	Secure headers middleware (X-Content-Type-Options, X-Frame-Options, CSP)
	•	Rate limiting and circuit breaker to prevent API abuse
	•	SonarQube Scans – fixed code smells, validated against CWE standards
	•	GDPR-friendly – no personally identifiable data retained
	•	ISO 20022 XML output – audit-ready compliance format

This MVP is for research and compliance demonstration only.
It is not a financial product and should not be used for investment decisions.

⸻

📂 Example ISO 20022 Export

<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>HGUARD-RPT-20250903</MsgId>
      <CreDtTm>2025-09-03T12:34:56Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
      <DbtrAcct><Id><Othr><Id>0.0.1234</Id></Othr></Id></DbtrAcct>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="HBAR">100.00000000</InstdAmt></Amt>
        <RmtInf><Ustrd>HGuard AML/CFT Report</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>


⸻

📎 Quick Copy Buttons (Optional for Docs UI)

👉 Clone repo:

<button onclick="navigator.clipboard.writeText('git clone https://github.com/ADCoinX/Hguard-Hedera.git')" style="padding:6px 12px;background:#0f62fe;color:#fff;border:none;border-radius:6px;cursor:pointer;">
📋 Copy Clone Command
</button>

👉 Run server:

<button onclick="navigator.clipboard.writeText('uvicorn app.main:app --reload --port 8000')" style="padding:6px 12px;background:#16a34a;color:#fff;border:none;border-radius:6px;cursor:pointer;">
📋 Copy Run Command
</button>


⸻

✍️ Built with ❤️ by ADCX Lab
(Pioneers of CryptoGuard, AssetGuard AI, GuardianX)

---

This version is **grant-ready**:  
- English ✅  
- InfoSec section ✅  
- ISO compliance ✅  
- Developer quick-start ✅  

