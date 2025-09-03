# HGuard – Hedera Wallet Validator 🔒

**Current Date and Time (UTC):** 2025-09-03 03:06:23  
**Current User's Login:** ADCoinX

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
```

### Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

👉 UI available at: http://localhost:8000

⸻

## 🔌 Architecture Diagram

```
                                 +-------------------+
                                 |                   |
  +-----------------+            |   Hedera Network  |
  |                 |            |                   |
  |  User/Browser   |            +-------------------+
  |                 |                     |
  +-----------------+                     |
          |                               |
          v                               v
  +-----------------+            +-------------------+
  |                 |  API Call  |                   |
  |  HGuard FastAPI |<---------->| Hedera Mirror API |
  |  Application    |            |                   |
  |                 |            +-------------------+
  +-----------------+
          |
          v
  +-----------------------------+
  |                             |
  |  ISO 20022 XML Generation   |
  |  - pain.001 format          |
  |  - Wallet validation        |
  |  - Risk scoring             |
  |                             |
  +-----------------------------+
```

HGuard follows a simple, stateless architecture:

1. **Client Side**: Browser sends request with Hedera Account ID
2. **HGuard Server**: FastAPI application processes the request
3. **External API**: Application fetches live data from Hedera Mirror Node API
4. **Processing**: Risk scoring and validation logic is applied
5. **Response**: Results are returned to client or formatted as ISO 20022 XML

This architecture ensures high performance, security, and reliability with minimal infrastructure requirements.

⸻

## ⚙️ Environment Variables

APP_ENV=production  
LOG_LEVEL=info  
LOG_SALT=your_secret_salt  
PRIMARY_MIRROR_BASE=https://mainnet-public.mirrornode.hedera.com  
CB_FAILURE_THRESHOLD=5  
CB_RESET_SECONDS=30  
RATE_LIMIT_RPS=10  
ML_ENABLED=false  

⸻

## 📡 API Endpoints

Endpoint | Description  
---|---  
/ | UI Homepage  
/validate?accountId=0.0.xxxx | Validate Hedera wallet  
/export/iso20022/pain001?accountId=0.0.xxxx | Export ISO 20022 XML  
/metrics | Prometheus metrics  
/version | API version & timestamp  

⸻

## 🛡️ Security & InfoSec

HGuard was designed to be lightweight, stateless, and secure:  
- No private keys / seeds / PII stored – only public blockchain data is processed  
- TLS 1.3 + HSTS enforced at deployment (Render/HTTPS)  
- Secure headers middleware (X-Content-Type-Options, X-Frame-Options, CSP)  
- Rate limiting and circuit breaker to prevent API abuse  
- SonarQube Scans – fixed code smells, validated against CWE standards  
- GDPR-friendly – no personally identifiable data retained  
- ISO 20022 XML output – audit-ready compliance format  

This MVP is for research and compliance demonstration only.  
It is not a financial product and should not be used for investment decisions.

⸻

## 📂 Example ISO 20022 Export

```xml
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
```

⸻

## 📎 Quick Copy Buttons (Optional for Docs UI)

👉 Clone repo:

<button onclick="navigator.clipboard.writeText('git clone https://github.com/ADCoinX/Hguard-Hedera.git')" style="padding:6px 12px;background:#0f62fe;color:#fff;border:none;border-radius:6px;cursor:pointer;">
📋 Copy Clone Command
</button>

👉 Run server:

<button onclick="navigator.clipboard.writeText('uvicorn app.main:app --reload --port 8000')" style="padding:6px 12px;background:#16a34a;color:#fff;border:none;border-radius:6px;cursor:pointer;">
📋 Copy Run Command
</button>

⸻

## ⚖️ Disclaimer

- This MVP is for research and compliance demonstration purposes only.
- No private keys, seed phrases, or PII are stored or processed.
- Outputs, including risk scoring, are informational and **not** financial advice.
- ADCX Lab and HGuard are not liable for any loss or damages arising from use of this tool.
- The ISO 20022 XML export is for compliance and audit demonstration; it is **not** a regulated product.

⸻

## 📄 License (MIT)

```
MIT License

Copyright (c) 2025 ADCX Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

⸻

✍️ Built with ❤️ by ADCX Lab  
(Pioneers of CryptoGuard, AssetGuard AI, GuardianX)

---

This version is **grant-ready**:  
- English ✅  
- InfoSec section ✅  
- ISO compliance ✅  
- Developer quick-start ✅  
- Architecture diagram ✅  
- Disclaimer ✅  
- MIT License ✅  
