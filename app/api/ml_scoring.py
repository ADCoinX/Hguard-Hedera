import os
import math
from typing import List, Tuple, Dict, Any

# --- Env Flags ---
ML_ENABLED: bool = os.getenv("ML_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
ML_RANDOM_SEED: int = int(os.getenv("ML_RANDOM_SEED", "42"))
ML_CONTAMINATION: float = float(os.getenv("ML_CONTAMINATION", "0.2"))  # 0–0.5 safe

_clf = None  # lazy init global model


# --- Internal Helpers ---
def _train_if_needed() -> None:
    """Train IsolationForest only once, no side effects on import."""
    global _clf
    if _clf is not None or not ML_ENABLED:
        return
    try:
        from sklearn.ensemble import IsolationForest
        import numpy as np

        train_data = np.array(
            [
                [10, 5, 0.0],
                [1000, 20, 0.05],
                [500, 15, 0.10],
                [0, 0, 0.0],
                [5, 1, 0.0],
                [0, 0, 1.0],
                [2, 2, 0.5],
                [10_000, 100, 0.0],
                [50, 0, 0.0],
                [0, 10, 0.9],
            ],
            dtype=float,
        )

        # FIX: Provide a seed for the random_state parameter for reproducibility
        _clf = IsolationForest(
            n_estimators=100,
            contamination=max(0.0, min(ML_CONTAMINATION, 0.5)),
            random_state=ML_RANDOM_SEED,  # always use a fixed seed
            n_jobs=1,
        )
        _clf.fit(train_data)
    except Exception as e:
        # Fail-safe: disable ML cleanly
        _clf = None


def _coerce_float(x: Any) -> float:
    """Convert to float safely; NaN/inf → 0.0"""
    try:
        v = float(x)
        if math.isfinite(v):
            return v
        return 0.0
    except Exception:
        return 0.0


# --- Public API ---
def extract_simple_features(account: Dict[str, Any], last5: Any) -> List[float]:
    """Return [balance, tx_count, failed_ratio]"""
    balance = _coerce_float(account.get("balance", 0))

    if isinstance(last5, list):
        txs = last5
    elif isinstance(last5, dict):
        txs = last5.get("transactions", []) or []
    else:
        txs = []

    txs = [t for t in txs if isinstance(t, dict)]
    tx_count = len(txs)
    failed_count = sum(1 for tx in txs if (tx.get("result") or "").upper() == "FAIL")
    failed_ratio = (failed_count / tx_count) if tx_count > 0 else 0.0

    return [balance, float(tx_count), failed_ratio]


def ml_adjust_simple(account_json: Dict[str, Any], tx_json: Any) -> Tuple[int, List[str]]:
    """
    Adjust risk score via IsolationForest ML.
    Returns (delta_score, flags).
    Never raises exceptions — always safe.
    """
    if not ML_ENABLED:
        return 0, []

    try:
        _train_if_needed()
        if _clf is None:
            return 0, ["ML_DISABLED"]

        import numpy as np
        feats = np.array([extract_simple_features(account_json, tx_json)], dtype=float)
        pred = int(_clf.predict(feats)[0])  # -1 anomaly, 1 normal

        if pred == -1:
            return -10, ["ML_ANOMALY"]
        return 5, ["ML_NORMAL"]

    except Exception as e:
        # Fail-safe: fallback
        return 0, ["ML_FALLBACK"]
