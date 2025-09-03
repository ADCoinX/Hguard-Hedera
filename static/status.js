// /static/status.js
const $ = (id) => document.getElementById(id);

async function safeFetch(url){
  const res = await fetch(url,{cache:"no-store"});
  const text = await res.text();
  let json=null; try{ json=JSON.parse(text);}catch{}
  return {ok:res.ok,json,text};
}
function setPill(id,state,text){
  const el=$(id); if(!el) return;
  el.classList.remove("ok","warn","err");
  if(state) el.classList.add(state);
  el.querySelector("strong").textContent=text;
}
function fmtUptime(sec){
  const s=Number(sec); if(Number.isNaN(s)) return String(sec);
  const d=Math.floor(s/86400),h=Math.floor((s%86400)/3600),m=Math.floor((s%3600)/60);
  if(d>0) return `${d}d ${h}h`; if(h>0) return `${h}h ${m}m`; return `${m}m`;
}
function parseRequests(text){
  const tries=[
    /hguard_requests_total\s+(\d+(?:\.\d+)?)/i,
    /http_requests_total\s+(\d+(?:\.\d+)?)/i,
    /requests_total\s+(\d+(?:\.\d+)?)/i
  ];
  for(const re of tries){ const m=text.match(re); if(m) return Number(m[1]); }
  return null;
}

async function refreshStatus(){
  // Health (support /healthz too)
  try{
    let h = await safeFetch("/health");
    if(!h.ok) h = await safeFetch("/healthz");
    if(h.ok){
      const up = h.json && (h.json.uptime_seconds||h.json.uptime||h.json.uptimeSec);
      setPill("status-health","ok", up?`OK • ${fmtUptime(up)}`:"OK");
    } else setPill("status-health","err","Down");
  }catch{ setPill("status-health","err","Down"); }

  // Version
  try{
    const v=await safeFetch("/version");
    let ver="unknown";
    if(v.json && (v.json.version||v.json.app||v.json.tag)) ver=v.json.version||v.json.app||v.json.tag;
    else if(v.text) ver=v.text.trim().slice(0,24);
    setPill("status-version","ok",ver);
  }catch{ setPill("status-version","warn","unknown"); }

  // Metrics
  try{
    const m=await safeFetch("/metrics");
    if(m.ok){
      const req=parseRequests(m.text);
      setPill("status-metrics","ok", req!=null?`${req.toLocaleString()} total`:"Available");
    } else setPill("status-metrics","warn","Unavailable");
  }catch{ setPill("status-metrics","warn","Unavailable"); }
}

document.addEventListener("DOMContentLoaded", ()=>{
  refreshStatus();
  setInterval(refreshStatus, 45000);

  // fail-safe if script loaded but endpoints unreachable
  setTimeout(()=>{
    const el=document.getElementById("status-health");
    if(el && el.textContent.includes("Checking")) {
      el.classList.add("warn");
      el.querySelector("strong").textContent="Unavailable";
    }
  }, 4000);
});
