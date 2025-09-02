import os

ML_ENABLED = os.getenv("ML_ENABLED", "false").lower() in ("1", "true", "yes", "on")

try:
    if ML_ENABLED:
        from sklearn.ensemble import IsolationForest
        import numpy as np

        # Synthetic training set: mostly normal, some anomalies
        # Features: [balance, tx_count, failed_ratio]
        train_data = [
            [10, 5, 0.0], [1000, 20, 0.05], [500, 15, 0.1], [0, 0, 0.0], [5, 1, 0.0],
            [0, 0, 1.0], [2, 2, 0.5], [10000, 100, 0.0], [50, 0, 0.0], [0, 10, 0.9]
        ]
        clf = IsolationForest(n_estimators=30, contamination=0.2)
        clf.fit(train_data)
    else:
        clf = None
except Exception:
    clf = None
    ML_ENABLED = False

def extract_simple_features(account, last5):
    balance = float(account.get("balance", 0))
    txs = last5 if isinstance(last5, list) else last5.get("transactions", [])
    tx_count = len(txs)
    failed_count = sum(1 for tx in txs if tx.get("result") == "FAIL")
    failed_ratio = (failed_count / tx_count) if tx_count > 0 else 0
    return [balance, tx_count, failed_ratio]

def ml_adjust_simple(account_json, tx_json):
    if not ML_ENABLED or not clf:
        return 0, []
    feats = [extract_simple_features(account_json, tx_json)]
    try:
        pred = clf.predict(feats)[0]  # -1: anomaly, 1: normal
        if pred == -1:
            return -10, ["ML_ANOMALY"]
        else:
            return 5, ["ML_NORMAL"]
    except Exception:
        return 0, []