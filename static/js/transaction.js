/**
 * transaction.js — Handles the new transaction form and
 *                  displays the AI threat result inline.
 */

document.addEventListener("DOMContentLoaded", async () => {
  await checkAuth();

  const form = document.getElementById("txn-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearFieldErrors("amount-error", "location-error", "device-error");
    ["amount", "location", "device_info"].forEach(markValid);

    const amount     = parseFloat(document.getElementById("amount").value);
    const location   = document.getElementById("location").value;
    const device     = document.getElementById("device_info").value;
    const is_foreign = document.getElementById("is_foreign").checked ? 1 : 0;

    let valid = true;

    if (!amount || amount <= 0) {
      showFieldError("amount-error", "Enter a valid positive amount");
      markInvalid("amount"); valid = false;
    }
    if (amount > 1_000_000) {
      showFieldError("amount-error", "Amount exceeds maximum limit of ₹10,00,000");
      markInvalid("amount"); valid = false;
    }
    if (!location) {
      showFieldError("location-error", "Select a location");
      markInvalid("location"); valid = false;
    }
    if (!device) {
      showFieldError("device-error", "Select a device");
      markInvalid("device_info"); valid = false;
    }
    if (!valid) return;

    setLoading("txn-btn", true);

    try {
      const res  = await fetch(`${API}/api/transactions`, {
        method     : "POST",
        headers    : { "Content-Type": "application/json" },
        credentials: "include",
        body       : JSON.stringify({ amount, location, device_info: device, is_foreign })
      });
      const data = await res.json();

      if (!res.ok) {
        showAlert("txn-alert", "error", "❌ " + (data.error || "Transaction failed"));
        return;
      }

      // Show result using a large popup
      showThreatResultModal(data);
      form.reset();

    } catch {
      showAlert("txn-alert", "error", "❌ Network error — is the server running?");
    } finally {
      setLoading("txn-btn", false);
    }
  });
});

function showThreatResultModal(data) {
  // Build a full-screen result overlay
  const risk  = data.risk_level;
  const prob  = data.fraud_probability;
  const alert = data.alert;

  const colorMap = {
    LOW   : { color: "#00c9a7", bg: "rgba(0,201,167,.12)", icon: "✅" },
    MEDIUM: { color: "#ffc107", bg: "rgba(255,193,7,.12)",  icon: "⚠️" },
    HIGH  : { color: "#ff4d6d", bg: "rgba(255,77,109,.12)", icon: "🚨" },
  };
  const c = colorMap[risk] || colorMap.LOW;

  const overlay = document.createElement("div");
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:9999;
    background:rgba(0,0,0,.7);backdrop-filter:blur(6px);
    display:flex;align-items:center;justify-content:center;
  `;

  overlay.innerHTML = `
    <div style="
      background:#111520;border:1px solid ${c.color};border-radius:18px;
      padding:40px;max-width:460px;width:90%;text-align:center;
      box-shadow:0 24px 60px rgba(0,0,0,.6);animation:slideIn .3s ease;
    ">
      <div style="font-size:52px;margin-bottom:12px;">${c.icon}</div>
      <div style="
        display:inline-block;background:${c.bg};border:1px solid ${c.color};
        color:${c.color};border-radius:999px;padding:6px 20px;
        font-weight:700;font-size:15px;letter-spacing:1px;margin-bottom:20px;
      ">${risk} RISK</div>

      <h2 style="font-family:'Syne',sans-serif;font-size:22px;margin-bottom:8px;">
        Transaction #${data.transaction_id}
      </h2>
      <p style="color:#7a84a0;margin-bottom:24px;">${data.message}</p>

      <div style="background:#0a0d14;border-radius:12px;padding:20px;text-align:left;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.06);">
          <span style="color:#7a84a0;font-size:14px;">Amount</span>
          <span style="font-weight:600;">${formatCurrency(data.amount)}</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.06);">
          <span style="color:#7a84a0;font-size:14px;">Fraud Probability</span>
          <span style="font-weight:600;color:${c.color};">${prob}%</span>
        </div>
        <div style="padding:10px 0;">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="color:#7a84a0;font-size:14px;">Risk Level</span>
            <span style="font-weight:600;color:${c.color};">${risk}</span>
          </div>
          <div style="height:6px;background:rgba(255,255,255,.08);border-radius:3px;">
            <div style="height:100%;width:${prob}%;background:${c.color};border-radius:3px;transition:width .5s;"></div>
          </div>
        </div>
      </div>

      ${alert ? `
        <div style="
          background:rgba(255,77,109,.12);border:1px solid rgba(255,77,109,.3);
          border-radius:10px;padding:14px;margin-bottom:20px;
          color:#ff4d6d;font-size:14px;
        ">
          🚨 <strong>Security Alert!</strong> This transaction has been flagged.
          Please verify with your bank if you did not initiate this.
        </div>
      ` : ""}

      <div style="display:flex;gap:12px;justify-content:center;">
        <button onclick="this.closest('[style*=fixed]').remove()"
          style="
            background:rgba(79,142,247,.15);border:1px solid rgba(79,142,247,.3);
            color:#4f8ef7;padding:12px 24px;border-radius:8px;
            font-family:'Syne',sans-serif;font-weight:600;cursor:pointer;
          ">Close</button>
        <a href="/threat-result"
          style="
            background:#4f8ef7;color:#fff;padding:12px 24px;border-radius:8px;
            font-family:'Syne',sans-serif;font-weight:600;text-decoration:none;
            display:inline-flex;align-items:center;
          ">View All Logs →</a>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });
}
