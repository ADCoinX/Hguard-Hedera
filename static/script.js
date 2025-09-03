const form = document.getElementById('validateForm');
const resultCard = document.getElementById('resultCard');
let currentAccount = "";

form.onsubmit = async e => {
    e.preventDefault();
    const accountId = form.accountId.value;
    const button = document.getElementById('validateBtn');
    button.textContent = 'Validating...';
    button.disabled = true;

    try {
        const resp = await fetch(`/validate?accountId=${encodeURIComponent(accountId)}`);
        const data = await resp.json();

        if (!resp.ok) {
            alert(data.detail || "Validation failed.");
            resultCard.style.display = 'none';
            return;
        }
        
        document.getElementById('balance').textContent = `${(data.balanceTinybar / 100_000_000).toLocaleString()} HBAR`;
        document.getElementById('txCount').textContent = data.txCount;
        document.getElementById('scoreBadge').textContent = `${data.score} / 100`;
        document.getElementById('last5Tx').innerHTML = (data.last5Tx || [])
            .map(tx => `<li>${tx.transaction_id}: ${tx.result}</li>`).join('');
        document.getElementById('flags').textContent = (data.flags || []).join(", ");
        
        resultCard.style.display = 'block';
        currentAccount = data.accountId;

    } catch (err) {
        alert("An error occurred. Please check the console.");
        console.error(err);
    } finally {
        button.textContent = 'Validate Wallet';
        button.disabled = false;
    }
};

document.getElementById('exportBtn').onclick = () => {
    if (!currentAccount) return;
    window.open(`/export/iso20022/pain001?accountId=${encodeURIComponent(currentAccount)}`, "_blank");
};

const disclaimerLink = document.getElementById('disclaimerLink');
const disclaimerModal = document.getElementById('disclaimerModal');
const closeDisclaimer = document.getElementById('closeDisclaimer');

disclaimerLink.onclick = (e) => {
    e.preventDefault();
    disclaimerModal.style.display = 'flex';
};
closeDisclaimer.onclick = () => {
    disclaimerModal.style.display = 'none';
};
window.onclick = (e) => {
    if (e.target == disclaimerModal) {
        disclaimerModal.style.display = 'none';
    }
};

const form = document.getElementById('validateForm');
const resultCard = document.getElementById('resultCard');
let currentAccount = "";

form.onsubmit = async e => {
    e.preventDefault();
    const accountId = form.accountId.value;
    const button = document.getElementById('validateBtn');
    button.textContent = 'Validating...';
    button.disabled = true;

    try {
        const resp = await fetch(`/validate?accountId=${encodeURIComponent(accountId)}`);
        const data = await resp.json();

        if (!resp.ok) {
            alert(data.detail || "Validation failed.");
            resultCard.style.display = 'none';
            return;
        }
        
        document.getElementById('balance').textContent = `${(data.balanceTinybar / 100_000_000).toLocaleString()} HBAR`;
        document.getElementById('txCount').textContent = data.txCount;
        document.getElementById('scoreBadge').textContent = `${data.score} / 100`;
        document.getElementById('last5Tx').innerHTML = (data.last5Tx || [])
            .map(tx => `<li>${tx.transaction_id}: ${tx.result}</li>`).join('');
        document.getElementById('flags').textContent = (data.flags || []).join(", ");
        
        resultCard.style.display = 'block';
        currentAccount = data.accountId;

    } catch (err) {
        alert("An error occurred. Please check the console.");
        console.error(err);
    } finally {
        button.textContent = 'Validate Wallet';
        button.disabled = false;
    }
};

document.getElementById('exportBtn').onclick = () => {
    if (!currentAccount) return;
    window.open(`/export/iso20022/pain001?accountId=${encodeURIComponent(currentAccount)}`, "_blank");
};

const disclaimerLink = document.getElementById('disclaimerLink');
const disclaimerModal = document.getElementById('disclaimerModal');
const closeDisclaimer = document.getElementById('closeDisclaimer');

disclaimerLink.onclick = (e) => {
    e.preventDefault();
    disclaimerModal.style.display = 'flex';
};
closeDisclaimer.onclick = () => {
    disclaimerModal.style.display = 'none';
};
window.onclick = (e) => {
    if (e.target == disclaimerModal) {
        disclaimerModal.style.display = 'none';
    }
};

