// /static/status.js
(() => {
  // ===== Helpers =====
  const $ = (id) => document.getElementById(id);

  async function safeFetch(url) {
    try {
      const res = await fetch(url, { cache: "no-store" });
      const text = await res.text();
      let json = null;
      try { json = JSON.parse(text); } catch {}
      return { ok: res.ok, json, text };
    } catch {
      return { ok: false, json: null, text: "" };
    }
  }

  function ensureStrong(el) {
    // Pastikan ada <strong> dalam anchor; kalau tak, buat
    if (!el) return null;
    let strong = el.querySelector("strong");
    if (!strong) {
      strong = document.createElement("strong");
      el.appendChild(document.createTextNode(" "));
      el.appendChild(strong);
    }
    return strong;
  }

  function setPill(id, state, text) {
    const el = $(id);
    if (!el) return;
    el.classList.remove("ok", "warn", "err");
    if (state) el.classList.add(state);
    const strong = ensureStrong(el);
    if (strong) strong.textContent = text;
  }

  function fmtUptime(sec) {
    const s = Number(sec);
    if (!Number.isFinite(s) || s < 0) return "";
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    if (d > 0) return `${d}d ${h}h`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m}m`;
  }

  function parseRequests(text) {
    // Cuba beberapa nama metric; ambil yang pertama match
    const patterns = [
      /hguard_requests_total\s+(\d+(?:\.\d+)?)/i,
      /http_requests_total\s+(\d+(?:\.\d+)?)/i,
      /requests_total\s+(\d+(?:\.\d+)?)/i
    ];
    for (const re of patterns) {
      const m = text.match(re);
      if (m) return Number(m[1]);
    }
    return null;
  }

  function trimOneLine(s, max = 24) {
    return String(s || "").trim().replace(/\s+/g, " ").slice(0, max);
  }

  // ===== Main refresh =====
  async function refreshStatus() {
    // Health (support /health then fallback /healthz)
    try {
      let h = await safeFetch("/health");
      if (!h.ok) h = await safeFetch("/healthz");
      if (h.ok) {
        const up =
          (h.json && (h.json.uptime_seconds || h.json.uptime || h.json.uptimeSec)) ||
          null;
        const txt = up ? `OK • ${fmtUptime(up)}` : "OK";
        setPill("status-health", "ok", txt);
      } else {
        setPill("status-health", "err", "Down");
      }
    } catch {
      setPill("status-health", "err", "Down");
    }

    // Version
    try {
      const v = await safeFetch("/version");
      if (v.ok) {
        let ver =
          (v.json && (v.json.version || v.json.app || v.json.tag)) ||
          trimOneLine(v.text, 24) ||
          "unknown";
        // If timestamp available, append short time
        if (v.json && v.json.timestamp) {
          const ts = trimOneLine(v.json.timestamp, 19);
          ver = `${ver}`;
        }
        setPill("status-version", "ok", ver);
      } else {
        setPill("status-version", "warn", "unknown");
      }
    } catch {
      setPill("status-version", "warn", "unknown");
    }

    // Metrics
    try {
      const m = await safeFetch("/metrics");
      if (m.ok) {
        const req = parseRequests(m.text);
        setPill("status-metrics", "ok", req != null ? `${req.toLocaleString()} total` : "Available");
      } else {
        setPill("status-metrics", "warn", "Unavailable");
      }
    } catch {
      setPill("status-metrics", "warn", "Unavailable");
    }
  }

  // ===== Init =====
  document.addEventListener("DOMContentLoaded", () => {
    // Fail-safe: jika selepas beberapa saat masih "Checking…", set Unavailable
    setTimeout(() => {
      const h = $("status-health");
      if (h && h.textContent.includes("Checking")) {
        h.classList.add("warn");
        ensureStrong(h).textContent = "Unavailable";
      }
    }, 4000);

    refreshStatus();
    setInterval(refreshStatus, 45000);
  });
})();
