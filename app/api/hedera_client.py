import httpx
import asyncio
import random
import time
from app.config import get_mirror_bases, CB_FAILURE_THRESHOLD, CB_RESET_SECONDS

# Circuit breaker state per host
_cb_state = {}

def _now():
    return time.monotonic()

def _host_key(base):
    return base

def _is_host_up(host):
    state = _cb_state.get(host)
    if not state:
        return True
    if state["fail_count"] < CB_FAILURE_THRESHOLD:
        return True
    # Check if reset period passed
    if _now() - state["down_since"] > CB_RESET_SECONDS:
        # Reset breaker
        _cb_state[host] = {"fail_count": 0, "down_since": None}
        return True
    return False

def _mark_host_failure(host):
    state = _cb_state.setdefault(host, {"fail_count": 0, "down_since": None})
    state["fail_count"] += 1
    if state["fail_count"] >= CB_FAILURE_THRESHOLD and not state["down_since"]:
        state["down_since"] = _now()

def _mark_host_success(host):
    _cb_state[host] = {"fail_count": 0, "down_since": None}

async def _fetch_json(url, client, host):
    attempts = 3
    for i in range(attempts):
        try:
            start = _now()
            resp = await client.get(url)
            latency = (_now() - start) * 1000
            resp.raise_for_status()
            data = resp.json()
            _mark_host_success(host)
            return data, latency
        except Exception:
            _mark_host_failure(host)
            # Exponential backoff + jitter
            backoff = (2 ** i) + random.uniform(0, 0.2)
            await asyncio.sleep(backoff)
    return None, 0

async def get_account(account_id: str) -> tuple[dict | None, str | None, float]:
    bases = get_mirror_bases()
    async with httpx.AsyncClient(timeout=2.0) as client:
        for base in bases:
            host = _host_key(base)
            if not _is_host_up(host):
                continue
            url = f"{base}/api/v1/accounts/{account_id}"
            data, latency = await _fetch_json(url, client, host)
            if data is not None:
                return data, base, latency
    return None, None, 0

async def get_last_txs(account_id: str, limit: int = 5) -> tuple[list, str | None, float]:
    bases = get_mirror_bases()
    limit = min(max(limit, 1), 5)
    async with httpx.AsyncClient(timeout=2.0) as client:
        for base in bases:
            host = _host_key(base)
            if not _is_host_up(host):
                continue
            url = f"{base}/api/v1/transactions?account.id={account_id}&order=desc&limit={limit}"
            data, latency = await _fetch_json(url, client, host)
            if data is not None and "transactions" in data:
                txs = data["transactions"][:limit]
                return txs, base, latency
    return [], None, 0