from decimal import Decimal, ROUND_DOWN

try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

def build_pain_001(account_id: str, balance_tinybar: int, now_ts: str) -> str:
    """
    Build ISO 20022 pain.001 XML string for a Hedera wallet balance.
    """
    # Convert tinybar to HBAR (divide by 1e8)
    hbar = Decimal(balance_tinybar) / Decimal("100000000")
    hbar_str = format(hbar.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN), "f")
    # Simple pain.001.001.11 skeleton
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.11">
    <CstmrCdtTrfInitn>
        <GrpHdr>
            <MsgId>{account_id}-{now_ts}</MsgId>
            <CreDtTm>{now_ts}T00:00:00Z</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>{hbar_str}</CtrlSum>
            <InitgPty>
                <Nm>Hedera Wallet Export</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>{account_id}-pmt</PmtInfId>
            <PmtMtd>TRF</PmtMtd>
            <BtchBookg>false</BtchBookg>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>{hbar_str}</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
            </PmtTpInf>
            <ReqdExctnDt>{now_ts}</ReqdExctnDt>
            <Dbtr>
                <Nm>{account_id}</Nm>
            </Dbtr>
            <DbtrAcct>
                <Id>
                    <Othr>
                        <Id>{account_id}</Id>
                    </Othr>
                </Id>
            </DbtrAcct>
            <CdtTrfTxInf>
                <Amt>
                    <InstdAmt Ccy="HBAR">{hbar_str}</InstdAmt>
                </Amt>
                <Cdtr>
                    <Nm>{account_id}</Nm>
                </Cdtr>
                <CdtrAcct>
                    <Id>
                        <Othr>
                            <Id>{account_id}</Id>
                        </Othr>
                    </Id>
                </CdtrAcct>
            </CdtTrfTxInf>
        </PmtInf>
    </CstmrCdtTrfInitn>
</Document>
"""
    # Optional XSD validation (if lxml and xsd available)
    # To validate, user must provide XSD file path
    return xml