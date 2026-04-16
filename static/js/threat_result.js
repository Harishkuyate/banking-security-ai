/**
 * threat_result.js — Loads and renders threat detection logs
 *                    with filter functionality and detail modal.
 */

let allLogs    = [];
let activeRisk = "ALL";

document.addEventListener("DOMContentLoaded", async () => {
  await checkAuth();
  await loadThreatLogs();
  setupFilters();
});

async function loadThreatLogs() {
  try {
    const res  = await fetch(`${API}/api/threat-logs`, { credentials: "include" });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Failed to load logs");

    allLogs = data;
    renderLogs(allLogs);

  } catch (err) {
    document.getElementById("threat-log-list").innerHTML =
      `<div class="table-loading" style="color:#ff4d6d;">Error: ${err.message}</div>`;
  }
}

function setupFilters() {
  document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeRisk = btn.dataset.risk;
      const filtered = activeRisk === "ALL"
        ? allLogs
        : allLogs.filter(l => l.risk_level === activeRisk);
      renderLogs(filtered);
    });
  });
}

function renderLogs(logs) {
  const container  = document.getElementById("threat-log-list");
  const emptyState = document.getElementById("empty-state");

  if (!logs || !logs.length) {
    container.innerHTML = "";
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");

  container.innerHTML = logs.map(log => {
    const prob     = parseFloat(log.fraud_probability || 0) * 100;
    const probCls  = log.risk_level === "HIGH" ? "high" : log.risk_level === "MEDIUM" ? "medium" : "low";

    return `
      <div class="threat-card risk-${log.risk_level}"
           onclick="openModal(${log.transaction_id})">
        <div class="tc-header">
          <span class="tc-id">Transaction #${log.transaction_id}</span>
          ${riskBadge(log.risk_level)}
        </div>
        <div class="tc-amount">${formatCurrency(log.amount)}</div>
        <div class="tc-meta">
          <div class="tc-row">
            <span>Location</span>
            <span>${log.location || "Unknown"}</span>
          </div>
          <div class="tc-row">
            <span>Status</span>
            <span>${log.status || "—"}</span>
          </div>
          <div class="tc-row">
            <span>Fraud Probability</span>
            <span style="color:${probCls === 'high' ? '#ff4d6d' : probCls === 'medium' ? '#ffc107' : '#00c9a7'}">
              ${prob.toFixed(1)}%
            </span>
          </div>
          <div class="tc-row">
            <span>Date</span>
            <span>${log.created_at || "—"}</span>
          </div>
        </div>
        <div class="prob-bar">
          <div class="prob-fill ${probCls}" style="width:${Math.min(prob,100)}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

async function openModal(txnId) {
  const modal   = document.getElementById("detail-modal");
  const content = document.getElementById("modal-content");

  content.innerHTML = `<div class="table-loading"><span class="spinner"></span> Loading...</div>`;
  modal.classList.remove("hidden");

  try {
    const res  = await fetch(`${API}/api/transactions/${txnId}`, { credentials: "include" });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error);

    const prob = parseFloat(data.fraud_probability || 0) * 100;

    content.innerHTML = `
      <div class="modal-row"><span>Transaction ID</span><span>#${data.id}</span></div>
      <div class="modal-row"><span>Amount</span><span>${formatCurrency(data.amount)}</span></div>
      <div class="modal-row"><span>Location</span><span>${data.location || "—"}</span></div>
      <div class="modal-row"><span>Device</span><span>${data.device_info || "—"}</span></div>
      <div class="modal-row"><span>Foreign Transaction</span><span>${data.is_foreign ? "Yes" : "No"}</span></div>
      <div class="modal-row"><span>Risk Level</span><span>${riskBadge(data.risk_level)}</span></div>
      <div class="modal-row"><span>Status</span><span>${statusBadge(data.status)}</span></div>
      <div class="modal-row"><span>Fraud Probability</span><span>${prob.toFixed(2)}%</span></div>
      <div class="modal-row"><span>Location Risk Factor</span><span>${data.location_risk ? "⚠️ High" : "✅ Low"}</span></div>
      <div class="modal-row"><span>Device Risk Factor</span><span>${data.device_risk ? "⚠️ High" : "✅ Low"}</span></div>
      <div class="modal-row"><span>Date & Time</span><span>${data.created_at || "—"}</span></div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color:#ff4d6d;">Error loading details: ${err.message}</p>`;
  }
}

function closeModal() {
  document.getElementById("detail-modal").classList.add("hidden");
}
