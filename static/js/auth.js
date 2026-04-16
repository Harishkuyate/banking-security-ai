/**
 * auth.js — Login & Registration logic
 * Handles form validation, API calls, password strength meter
 */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm    = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const pwInput      = document.getElementById("password");

  // ── Password strength meter ──────────────────────────────
  if (pwInput) {
    pwInput.addEventListener("input", () => {
      const fill = document.getElementById("pw-strength-fill");
      if (!fill) return;
      const val = pwInput.value;
      let score = 0;
      if (val.length >= 6)  score++;
      if (val.length >= 10) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      const pct   = (score / 5) * 100;
      const color = score <= 1 ? "#ff4d6d" : score <= 3 ? "#ffc107" : "#00c9a7";
      fill.style.width      = pct + "%";
      fill.style.background = color;
    });
  }

  // ── Login form ───────────────────────────────────────────
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearFieldErrors("email-error", "password-error");
      markValid("email"); markValid("password");

      const email    = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;

      let valid = true;

      if (!email) {
        showFieldError("email-error", "Email is required");
        markInvalid("email"); valid = false;
      } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        showFieldError("email-error", "Enter a valid email");
        markInvalid("email"); valid = false;
      }
      if (!password) {
        showFieldError("password-error", "Password is required");
        markInvalid("password"); valid = false;
      }
      if (!valid) return;

      setLoading("login-btn", true);
      try {
        const res  = await fetch(`${API}/api/login`, {
          method     : "POST",
          headers    : { "Content-Type": "application/json" },
          credentials: "include",
          body       : JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok) {
          showAlert("auth-alert", "success", "✅ Login successful! Redirecting...");
          setTimeout(() => window.location.href = "/dashboard", 800);
        } else {
          showAlert("auth-alert", "error", "❌ " + (data.error || "Login failed"));
        }
      } catch {
        showAlert("auth-alert", "error", "❌ Network error — is the server running?");
      } finally {
        setLoading("login-btn", false);
      }
    });
  }

  // ── Register form ────────────────────────────────────────
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearFieldErrors("name-error", "email-error", "password-error", "confirm-error");
      ["name","email","password","confirm_password"].forEach(markValid);

      const name     = document.getElementById("name").value.trim();
      const email    = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const confirm  = document.getElementById("confirm_password").value;

      let valid = true;

      if (!name || name.length < 2) {
        showFieldError("name-error", "Name must be at least 2 characters");
        markInvalid("name"); valid = false;
      }
      if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        showFieldError("email-error", "Enter a valid email address");
        markInvalid("email"); valid = false;
      }
      if (!password || password.length < 6) {
        showFieldError("password-error", "Password must be at least 6 characters");
        markInvalid("password"); valid = false;
      }
      if (password !== confirm) {
        showFieldError("confirm-error", "Passwords do not match");
        markInvalid("confirm_password"); valid = false;
      }
      if (!valid) return;

      setLoading("register-btn", true);
      try {
        const res  = await fetch(`${API}/api/register`, {
          method     : "POST",
          headers    : { "Content-Type": "application/json" },
          credentials: "include",
          body       : JSON.stringify({ name, email, password })
        });
        const data = await res.json();

        if (res.ok) {
          showAlert("auth-alert", "success", "✅ Account created! Redirecting...");
          setTimeout(() => window.location.href = "/dashboard", 800);
        } else {
          showAlert("auth-alert", "error", "❌ " + (data.error || "Registration failed"));
        }
      } catch {
        showAlert("auth-alert", "error", "❌ Network error — is the server running?");
      } finally {
        setLoading("register-btn", false);
      }
    });
  }
});
