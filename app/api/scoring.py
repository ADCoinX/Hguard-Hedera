from app.api.ml_scoring import ml_adjust_simple

def score(account_json, tx_json):
    flags = []
    score = 20

    # Extract features
    balance = float(account_json.get("balance", 0))
    txs = tx_json if isinstance(tx_json, list) else tx_json.get("transactions", [])
    tx_count = len(txs)
    failed_count = sum(1 for tx in txs if tx.get("result") == "FAIL")
    failed_ratio = (failed_count / tx_count) if tx_count > 0 else 0

    if balance > 0:
        score += 15
    if tx_count >= 1:
        score += 20
    if tx_count >= 10:
        score += 25
    if failed_ratio > 0.2:
        score -= 20
        flags.append("HIGH_FAILURE_RATIO")

    # ML adjustment
    ml_delta, ml_flags = ml_adjust_simple(account_json, tx_json)
    score += ml_delta
    score = max(0, min(100, score))
    flags.extend(ml_flags if ml_flags else [])

    return score, flags