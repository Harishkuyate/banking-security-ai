/**
 * dashboard.js — Loads stats, renders charts, populates table
 */

document.addEventListener("DOMContentLoaded", async () => {
  const user = await checkAuth();
  if (!user) return;

  document.getElementById("welcome-msg").textContent =
    `Hello, ${user.name} 👋 — Here's your security overview`;

  await loadDashboard();
});

async function loadDashboard() {
  try {
    const res  = await fetch(`${API}/api/dashboard/stats`, { credentials: "include" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to load stats");

    // ── KPI cards ──────────────────────────────────────────
    document.getElementById("kpi-total").textContent     = data.total_transactions;
    document.getElementById("kpi-amount").textContent    = formatCurrency(data.total_amount);
    document.getElementById("kpi-normal").textContent    = data.normal_count;
    document.getElementById("kpi-suspicious").textContent = data.suspicious_count;
    document.getElementById("model-acc").textContent     =
      data.model_accuracy !== "N/A"
        ? (parseFloat(data.model_accuracy) * 100).toFixed(1) + "%"
        : "Model not loaded";

    // ── Pie chart: risk distribution ──────────────────────
    const rb = data.risk_breakdown;
    renderPieChart(rb.LOW, rb.MEDIUM, rb.HIGH);

    // ── Bar chart: recent transactions ────────────────────
    renderBarChart(data.recent_transactions);

    // ── Table ─────────────────────────────────────────────
    renderTable(data.recent_transactions);

  } catch (err) {
    console.error(err);
  }
}

// ── Pie chart ─────────────────────────────────────────────
function renderPieChart(low, medium, high) {
  const ctx = document.getElementById("riskPieChart");
  if (!ctx) return;

  // Destroy existing instance if present
  if (ctx._chart) ctx._chart.destroy();

  ctx._chart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels  : ["Low Risk", "Medium Risk", "High Risk"],
      datasets: [{
        data           : [low || 0, medium || 0, high || 0],
        backgroundColor: ["rgba(0,201,167,.8)", "rgba(255,193,7,.8)", "rgba(255,77,109,.8)"],
        borderColor    : ["#00c9a7", "#ffc107", "#ff4d6d"],
        borderWidth    : 2,
        hoverOffset    : 6,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
          labels  : { color: "#7a84a0", padding: 14, font: { size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} transaction(s)`
          }
        }
      },
      cutout: "68%",
    }
  });
}

// ── Bar chart ─────────────────────────────────────────────
function renderBarChart(transactions) {
  const ctx = document.getElementById("txnBarChart");
  if (!ctx || !transactions || !transactions.length) return;

  if (ctx._chart) ctx._chart.destroy();

  const labels = transactions.map(t => `#${t.id}`).reverse();
  const amounts = transactions.map(t => parseFloat(t.amount)).reverse();
  const colors  = transactions.map(t =>
    t.risk_level === "HIGH"   ? "rgba(255,77,109,.8)" :
    t.risk_level === "MEDIUM" ? "rgba(255,193,7,.8)"  :
                                "rgba(0,201,167,.8)"
  ).reverse();

  ctx._chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label          : "Amount (₹)",
        data           : amounts,
        backgroundColor: colors,
        borderRadius   : 6,
        borderSkipped  : false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ₹ ${parseFloat(ctx.parsed.y).toLocaleString("en-IN")}`
          }
        }
      },
      scales: {
        x: { ticks: { color: "#7a84a0" }, grid: { color: "rgba(255,255,255,.04)" } },
        y: { ticks: { color: "#7a84a0" }, grid: { color: "rgba(255,255,255,.04)" } }
      }
    }
  });
}

// ── Transaction table ─────────────────────────────────────
function renderTable(transactions) {
  const tbody = document.getElementById("txn-body");
  if (!tbody) return;

  if (!transactions || !transactions.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="table-loading">No transactions yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = transactions.map(t => `
    <tr>
      <td>#${t.id}</td>
      <td>${formatCurrency(t.amount)}</td>
      <td>${t.location || "—"}</td>
      <td>${riskBadge(t.risk_level)}</td>
      <td>${statusBadge(t.status)}</td>
      <td>${t.created_at || "—"}</td>
      <td><a href="/threat-result" class="btn btn-sm btn-outline">View</a></td>
    </tr>
  `).join("");
}
