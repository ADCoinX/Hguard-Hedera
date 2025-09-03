// static/script.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('validateForm');
  const resultCard = document.getElementById('resultCard');
  const validateBtn = document.getElementById('validateBtn');
  const exportBtn = document.getElementById('exportBtn');
  const disclaimerLink = document.getElementById('disclaimerLink');
  const disclaimerModal = document.getElementById('disclaimerModal');
  const closeDisclaimer = document.getElementById('closeDisclaimer');

  let currentAccount = "";

  async function handleValidate(e) {
    if (e?.preventDefault) e.preventDefault();

    const accountId = form.accountId?.value?.trim() || "";
    if (!/^0\.0\.\d{1,20}$/.test(accountId)) {
      alert("Invalid Account ID format. Example: 0.0.123");
      return;
    }

    validateBtn.textContent = 'Validating...';
    validateBtn.disabled = true;

    try {
      const resp = await fetch(`/validate?accountId=${encodeURIComponent(accountId)}`, { cache: 'no-store' });
      // Cuba parse JSON walaupun error
      let data = null;
      try { data = await resp.json(); } catch { data = null; }

      if (!resp.ok) {
        alert((data && data.detail) || "Validation failed.");
        resultCard.style.display = 'none';
        return;
      }

      document.getElementById('balance').textContent =
        `${((data.balanceTinybar || 0) / 100_000_000).toLocaleString()} HBAR`;
      document.getElementById('txCount').textContent = data.txCount ?? '0';
      document.getElementById('scoreBadge').textContent = `${data.score ?? 0} / 100`;
      document.getElementById('last5Tx').innerHTML = (data.last5Tx || [])
        .map(tx => `<li>${tx.transaction_id}: ${tx.result}</li>`).join('');
      document.getElementById('flags').textContent = (data.flags || []).join(", ");

      resultCard.style.display = 'block';
      currentAccount = data.accountId || accountId;

    } catch (err) {
      console.error(err);
      alert("Network error. Please try again.");
      resultCard.style.display = 'none';
    } finally {
      validateBtn.textContent = 'Validate Wallet';
      validateBtn.disabled = false;
    }
  }

  // Bind: kalau button type="submit", submit akan kena; kalau type="button", click akan kena
  form.addEventListener('submit', handleValidate);
  validateBtn.addEventListener('click', handleValidate);

  // Export
  if (exportBtn) {
    exportBtn.onclick = () => {
      if (!currentAccount) return;
      window.open(`/export/iso20022/pain001?accountId=${encodeURIComponent(currentAccount)}`, "_blank");
    };
  }

  // Disclaimer
  if (disclaimerLink && disclaimerModal && closeDisclaimer) {
    disclaimerLink.onclick = (e) => { e.preventDefault(); disclaimerModal.style.display = 'flex'; };
    closeDisclaimer.onclick = () => { disclaimerModal.style.display = 'none'; };
    window.onclick = (e) => { if (e.target === disclaimerModal) disclaimerModal.style.display = 'none'; };
  }
});
