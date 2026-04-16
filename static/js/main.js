/**
 * main.js — Shared utilities for SecureBank AI
 * Handles: auth session check, logout, risk badge rendering, helpers
 */

// ── API base URL ────────────────────────────────────────────
const API = "";  // same origin; change to "http://localhost:5000" if needed

// ── Session check (runs on every protected page) ────────────
async function checkAuth() {
  try {
    const res = await fetch(`${API}/api/me`, { credentials: "include" });
    if (!res.ok) {
      window.location.href = "/login";
      return null;
    }
    return await res.json();
  } catch {
    window.location.href = "/login";
    return null;
  }
}

// ── Logout ──────────────────────────────────────────────────
async function logout() {
  await fetch(`${API}/api/logout`, { method: "POST", credentials: "include" });
  window.location.href = "/login";
}

// ── Risk badge HTML ─────────────────────────────────────────
function riskBadge(level) {
  const map = {
    LOW   : `<span class="badge-low">LOW</span>`,
    MEDIUM: `<span class="badge-med">MEDIUM</span>`,
    HIGH  : `<span class="badge-high">HIGH</span>`,
  };
  return map[level] || `<span>${level}</span>`;
}

// ── Status badge ────────────────────────────────────────────
function statusBadge(status) {
  if (status === "NORMAL") return `<span class="badge-low">✅ NORMAL</span>`;
  return `<span class="badge-high">⚠️ SUSPICIOUS</span>`;
}

// ── Format currency ─────────────────────────────────────────
function formatCurrency(amount) {
  return "₹ " + parseFloat(amount).toLocaleString("en-IN", {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

// ── Show alert banner ───────────────────────────────────────
function showAlert(elementId, type, message) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.className = `alert ${type}`;
  el.textContent = message;
}

// ── Toggle password visibility ──────────────────────────────
function togglePw(fieldId) {
  const inp = document.getElementById(fieldId);
  inp.type = inp.type === "password" ? "text" : "password";
}

// ── Set button loading state ────────────────────────────────
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn._origText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Processing...`;
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._origText || "Submit";
    btn.disabled = false;
  }
}

// ── Simple field validation helper ─────────────────────────
function showFieldError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.textContent = msg;
}
function clearFieldErrors(...ids) {
  ids.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = ""; });
}
function markInvalid(fieldId) {
  const el = document.getElementById(fieldId);
  if (el) el.classList.add("invalid");
}
function markValid(fieldId) {
  const el = document.getElementById(fieldId);
  if (el) el.classList.remove("invalid");
}
