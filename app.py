"""
=============================================================
  AI-Based Security Threat Detection System - Flask Backend
  File: app.py
  Description: REST API server for the banking security app.
               Handles auth, transactions, and ML inference.
=============================================================
  Run:  python app.py
  API:  http://localhost:5000
=============================================================
"""

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import mysql.connector
import bcrypt
import random
import joblib
import numpy as np
import json
import os
import re
from datetime import datetime
from functools import wraps

# ─── App Setup ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "banking_secret_key_2024_change_in_production"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app, supports_credentials=True)

# ─── Paths ───────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "ml", "fraud_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
META_PATH   = os.path.join(BASE_DIR, "ml", "model_meta.json")


# ─── Database Configuration ──────────────────────────────────
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "root",       # Change to your MySQL username
    "password": "Hari@1234",           # Change to your MySQL password
    "database": "banking_security",
    "port"    : 3306
}


def get_db():
    """Return a fresh MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ─── Load ML Model ───────────────────────────────────────────
model, scaler, model_meta = None, None, {}

def load_ml_model():
    global model, scaler, model_meta
    try:
        model  = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        with open(META_PATH) as f:
            model_meta = json.load(f)
        print("✅ ML model loaded successfully")
    except FileNotFoundError:
        print("⚠️  ML model not found — run ml/train_model.py first")


# ─── Helpers ─────────────────────────────────────────────────
def get_risk_level(prob: float) -> str:
    if prob < 0.30:
        return "LOW"
    elif prob < 0.65:
        return "MEDIUM"
    return "HIGH"


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))


def login_required(f):
    """Decorator: reject requests without a valid session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated
def generate_otp():
    return str(random.randint(100000, 999999))

# ─── HTML Page Routes ─────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/transaction")
def transaction_page():
    return render_template("transaction.html")

@app.route("/threat-result")
def threat_result_page():
    return render_template("threat_result.html")


# ─── API: Auth ────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    """Register a new user. Hashes password with bcrypt."""
    data = request.get_json()
    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    # Validation
    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400
    if len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters"}), 400
    if not validate_email(email):
        return jsonify({"error": "Invalid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        db  = get_db()
        cur = db.cursor()
        # Parameterised query prevents SQL injection
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed))
        db.commit()
        user_id = cur.lastrowid
        cur.close(); db.close()

        session["user_id"] = user_id
        session["name"]    = name
        return jsonify({"message": "Registration successful", "user_id": user_id}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid email or password"}), 401

    # ✅ OTP Generate
    otp = generate_otp()

    # Store temporarily
    session["temp_user_id"] = user["id"]
    session["otp"] = otp

    print("OTP:", otp)  # 👉 Terminal me dikhega (testing ke liye)

    return jsonify({"message": "OTP sent"})

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    user_otp = data.get("otp")

    # ❗ Check session exists
    if "otp" not in session or "temp_user_id" not in session:
        return jsonify({"error": "Session expired. Please login again."}), 400

    if user_otp == session["otp"]:
        # ✅ FINAL LOGIN
        session["user_id"] = session["temp_user_id"]

        # optional (for UI)
        session["name"] = "User"

        # cleanup
        session.pop("otp", None)
        session.pop("temp_user_id", None)

        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400
    """Authenticate user and create session."""
    data     = request.get_json()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close(); db.close()

        if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return jsonify({"error": "Invalid email or password"}), 401

        session["user_id"] = user["id"]
        session["name"]    = user["name"]
        return jsonify({"message": "Login successful",
                        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@app.route("/api/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user_id": session["user_id"], "name": session["name"]})


# ─── API: Transactions ───────────────────────────────────────
@app.route("/api/transactions", methods=["POST"])
@login_required
def add_transaction():
    """
    Add a transaction and immediately run fraud detection.
    Expected JSON body:
      amount, location, device_info, is_foreign (0/1)
    """
    data = request.get_json()

    try:
        amount   = float(data.get("amount", 0))
        location = (data.get("location") or "Unknown").strip()
        device   = (data.get("device_info") or "Unknown").strip()
        is_foreign = int(data.get("is_foreign", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid transaction data"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    if amount > 1_000_000:
        return jsonify({"error": "Amount exceeds maximum limit"}), 400

    # ── Build ML features ──────────────────────────────────────
    now           = datetime.now()
    hour          = now.hour
    day_of_week   = now.weekday()
    log_amount    = np.log1p(amount)
    odd_hour      = 1 if hour <= 5 else 0

    # Simple heuristic risk scores from inputs
    location_risk = 1 if location.lower() in ["unknown", "foreign", "international"] else 0
    device_risk   = 1 if device.lower() in ["unknown", "new device", "other"] else 0

    # velocity_score: simplified (real system would check DB history)
    velocity_score = min(int(amount / 1000), 10)

    composite_risk = location_risk + device_risk + is_foreign + odd_hour

    features = np.array([[
        amount, hour, day_of_week, location_risk, device_risk,
        is_foreign, velocity_score, log_amount, odd_hour, composite_risk
    ]])

    # ── ML Inference ───────────────────────────────────────────
    fraud_probability = 0.1   # fallback
    risk_level        = "LOW"

    if model and scaler:
        scaled = scaler.transform(features)
        fraud_probability = float(model.predict_proba(scaled)[0][1])
        risk_level        = get_risk_level(fraud_probability)

        status = "SUSPICIOUS" if risk_level in ("MEDIUM", "HIGH") else "NORMAL"

    # ── Risk-based Tips ─────────────────────────────
    if risk_level == "LOW":
        tips = [
            "Transaction appears normal and matches your usual activity.",
            "Ensure you are using a secure and trusted network.",
            "Keep monitoring your account regularly for any unusual activity.",
            "Avoid sharing your banking credentials with anyone."
        ]

    elif risk_level == "MEDIUM":
        tips = [
            "Verify the transaction details before proceeding.",
            "Check if the device or location is recognized.",
            "Enable two-factor authentication (2FA) for extra security.",
            "Monitor your account closely for suspicious activity."
        ]

    elif risk_level == "HIGH":
        tips = [
            "Do NOT proceed with this transaction immediately.",
            "Contact your bank or customer support right away.",
            "Change your account password and secure your account.",
            "Block your card or account if you suspect fraud."
        ]

    try:
        db  = get_db()
        cur = db.cursor()

        # Insert transaction (parameterised — no SQL injection risk)
        cur.execute(
            """INSERT INTO transactions
               (user_id, amount, location, device_info, is_foreign,
                status, fraud_probability, risk_level, created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (session["user_id"], amount, location, device, is_foreign,
             status, fraud_probability, risk_level, now)
        )
        txn_id = cur.lastrowid

        # Insert threat log
        cur.execute(
            """INSERT INTO threat_logs
               (transaction_id, risk_level, fraud_probability,
                location_risk, device_risk, is_foreign, created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (txn_id, risk_level, fraud_probability,
             location_risk, device_risk, is_foreign, now)
        )
        db.commit()
        cur.close(); db.close()

        return jsonify({
    "transaction_id"  : txn_id,
    "amount"          : amount,
    "status"          : status,
    "risk_level"      : risk_level,
    "fraud_probability": round(fraud_probability * 100, 2),
    "alert"           : risk_level in ("MEDIUM", "HIGH"),
    "tips"            : tips,
    "message"         : (
        "⚠️ Suspicious activity detected! Please verify this transaction."
        if status == "SUSPICIOUS"
        else "✅ Transaction processed successfully."
    )
}), 201

    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    """Fetch all transactions for the logged-in user."""
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT t.*, tl.fraud_probability as fp
               FROM transactions t
               LEFT JOIN threat_logs tl ON tl.transaction_id = t.id
               WHERE t.user_id = %s
               ORDER BY t.created_at DESC
               LIMIT 50""",
            (session["user_id"],)
        )
        rows = cur.fetchall()
        cur.close(); db.close()

        # Serialise datetime objects
        for r in rows:
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(rows)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/transactions/<int:txn_id>", methods=["GET"])
@login_required
def get_transaction(txn_id):
    """Fetch a single transaction with its threat log."""
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT t.*, tl.fraud_probability, tl.location_risk,
                      tl.device_risk, tl.is_foreign as tl_foreign
               FROM transactions t
               LEFT JOIN threat_logs tl ON tl.transaction_id = t.id
               WHERE t.id = %s AND t.user_id = %s""",
            (txn_id, session["user_id"])
        )
        row = cur.fetchone()
        cur.close(); db.close()

        if not row:
            return jsonify({"error": "Transaction not found"}), 404

        if isinstance(row.get("created_at"), datetime):
            row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(row)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── API: Dashboard Stats ─────────────────────────────────────
@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    """Return summary stats and chart data for the dashboard."""
    uid = session["user_id"]
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)

        # Overview counts
        cur.execute("SELECT COUNT(*) as total, SUM(amount) as total_amount FROM transactions WHERE user_id=%s", (uid,))
        overview = cur.fetchone()

        cur.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id=%s AND status='NORMAL'",    (uid,))
        normal = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id=%s AND status='SUSPICIOUS'", (uid,))
        suspicious = cur.fetchone()["cnt"]

        # Risk breakdown
        cur.execute(
            "SELECT risk_level, COUNT(*) as cnt FROM transactions WHERE user_id=%s GROUP BY risk_level",
            (uid,)
        )
        risk_data = {r["risk_level"]: r["cnt"] for r in cur.fetchall()}

        # Last 7 transactions
        cur.execute(
            "SELECT id, amount, status, risk_level, created_at FROM transactions WHERE user_id=%s ORDER BY created_at DESC LIMIT 7",
            (uid,)
        )
        recent = cur.fetchall()
        for r in recent:
            if isinstance(r.get("created_at"), datetime):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M")

        cur.close(); db.close()

        return jsonify({
            "total_transactions": overview["total"]      or 0,
            "total_amount"      : float(overview["total_amount"] or 0),
            "normal_count"      : normal,
            "suspicious_count"  : suspicious,
            "risk_breakdown"    : {
                "LOW"   : risk_data.get("LOW",    0),
                "MEDIUM": risk_data.get("MEDIUM", 0),
                "HIGH"  : risk_data.get("HIGH",   0),
            },
            "recent_transactions": recent,
            "model_accuracy"    : model_meta.get("accuracy", "N/A"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── API: Threat Logs ─────────────────────────────────────────
@app.route("/api/threat-logs", methods=["GET"])
@login_required
def get_threat_logs():
    uid = session["user_id"]
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            """SELECT tl.*, t.amount, t.location, t.status
               FROM threat_logs tl
               JOIN transactions t ON t.id = tl.transaction_id
               WHERE t.user_id = %s
               ORDER BY tl.created_at DESC LIMIT 20""",
            (uid,)
        )
        logs = cur.fetchall()
        cur.close(); db.close()

        for l in logs:
            if isinstance(l.get("created_at"), datetime):
                l["created_at"] = l["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify(logs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Health Check ─────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status"      : "ok",
        "model_loaded": model is not None,
        "timestamp"   : datetime.now().isoformat()
    })


# ─── Entry Point ─────────────────────────────────────────────
if __name__ == "__main__":
    load_ml_model()
    app.run(debug=True, host="0.0.0.0", port=5001)
