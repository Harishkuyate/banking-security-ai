# 🛡 SecureBank AI — AI-Based Security Threat Detection System

> A full-stack banking security application that uses **Machine Learning (Random Forest)** to detect fraudulent transactions in real-time.

---

## 📁 Folder Structure

```
banking_security/
│
├── app.py                        # Flask backend — all REST APIs
├── requirements.txt              # Python dependencies
│
├── ml/
│   ├── train_model.py            # Model training script
│   ├── transactions_dataset.csv  # Sample training dataset (100 rows)
│   ├── fraud_model.pkl           # Trained model (generated after training)
│   ├── scaler.pkl                # Feature scaler (generated after training)
│   └── model_meta.json           # Accuracy & feature info (generated)
│
├── database/
│   └── setup.sql                 # MySQL table creation script
│
├── templates/                    # Jinja2 HTML templates
│   ├── index.html                # Home / landing page
│   ├── login.html                # Sign-in page
│   ├── register.html             # Registration page
│   ├── dashboard.html            # Main dashboard with charts
│   ├── transaction.html          # Add new transaction
│   └── threat_result.html        # Threat detection logs
│
├── static/
│   ├── css/
│   │   └── main.css              # Complete dark-theme stylesheet
│   └── js/
│       ├── main.js               # Shared utilities (auth, formatters)
│       ├── auth.js               # Login & register logic
│       ├── dashboard.js          # Chart.js charts + KPI loading
│       ├── transaction.js        # Transaction form + result modal
│       └── threat_result.js      # Threat log rendering + filters
│
└── tests/
    ├── test_app.py               # Pytest unit & integration tests
    └── postman_collection.json   # Postman API collection
```

---

## ⚙️ Local Setup Guide

### Step 1 — Install XAMPP and Start MySQL

1. Download XAMPP from https://www.apachefriends.org/
2. Open XAMPP Control Panel
3. Start **Apache** and **MySQL**
4. Open **phpMyAdmin** at http://localhost/phpmyadmin

### Step 2 — Create the Database

**Option A — phpMyAdmin (GUI):**
1. Click **"New"** in the left sidebar
2. Name it `banking_security`, click **Create**
3. Click the **SQL** tab
4. Paste the contents of `database/setup.sql`
5. Click **Go**

**Option B — MySQL CLI:**
```bash
mysql -u root -p < database/setup.sql
```

### Step 3 — Configure Database Credentials

Open `app.py` and update the `DB_CONFIG` block:

```python
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "root",        # Your MySQL username
    "password": "",            # Your MySQL password (blank for XAMPP default)
    "database": "banking_security",
    "port"    : 3306
}
```

### Step 4 — Create Python Virtual Environment

```bash
cd banking_security

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### Step 5 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 6 — Train the Machine Learning Model

```bash
python ml/train_model.py
```

**Expected output:**
```
📂 Loading dataset...
   Rows: 100 | Columns: [...]
   Fraud rate: 36.0%

📊 Train size: 80 | Test size: 20

🤖 Training Random Forest classifier...
   Training complete!

══════════════════════════════════════════════════
  MODEL EVALUATION RESULTS
══════════════════════════════════════════════════
  Accuracy : 95.00%
  ROC-AUC  : 0.9800

✅ Model saved  → ml/fraud_model.pkl
✅ Scaler saved → ml/scaler.pkl
✅ Meta saved   → ml/model_meta.json
```

### Step 7 — Run the Flask Server

```bash
python app.py
```

You should see:
```
✅ ML model loaded successfully
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 8 — Open the Application

Visit: **http://localhost:5000**

---

## 🚀 Application Pages

| URL | Page |
|-----|------|
| `http://localhost:5000/` | Home / Landing Page |
| `http://localhost:5000/register` | Create Account |
| `http://localhost:5000/login` | Sign In |
| `http://localhost:5000/dashboard` | Dashboard + Charts |
| `http://localhost:5000/transaction` | Add Transaction |
| `http://localhost:5000/threat-result` | Threat Detection Logs |

---

## 🔌 REST API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET  | `/api/health`            | ❌ | Server + model health check |
| POST | `/api/register`          | ❌ | Create new user account |
| POST | `/api/login`             | ❌ | Login and create session |
| POST | `/api/logout`            | ✅ | Destroy session |
| GET  | `/api/me`                | ✅ | Get current user info |
| POST | `/api/transactions`      | ✅ | Add transaction + run AI detection |
| GET  | `/api/transactions`      | ✅ | List all transactions |
| GET  | `/api/transactions/<id>` | ✅ | Get single transaction details |
| GET  | `/api/dashboard/stats`   | ✅ | KPIs, chart data, recent txns |
| GET  | `/api/threat-logs`       | ✅ | All AI threat analysis logs |

---

## 🧪 Testing with Postman

1. Open Postman → **Import** → select `tests/postman_collection.json`
2. Run requests **in order**:
   - Health Check ✅ (no auth needed)
   - Register User
   - Login (Postman automatically saves the session cookie)
   - Add Normal Transaction → expect `LOW` risk
   - Add Suspicious Transaction → expect `MEDIUM`/`HIGH` risk
   - Get All Transactions
   - Dashboard Stats
   - Get Threat Logs
   - Logout

> **Important:** Enable **"Send cookies"** in Postman settings for session authentication to work.

---

## 🧪 Running Unit Tests

```bash
# Install pytest
pip install pytest

# Run all tests
python -m pytest tests/test_app.py -v

# Run a specific test class
python -m pytest tests/test_app.py::TestTransactions -v
```

---

## 🤖 Machine Learning Model Details

| Property | Value |
|----------|-------|
| Algorithm | Random Forest (200 trees) |
| Library | Scikit-learn |
| Features | amount, hour, day_of_week, location_risk, device_risk, is_foreign, velocity_score, log_amount, odd_hour, composite_risk |
| Output | Fraud probability (0–1) |
| Risk Mapping | `< 0.30` → LOW · `0.30–0.65` → MEDIUM · `> 0.65` → HIGH |

**Feature descriptions:**

| Feature | Description |
|---------|-------------|
| `amount` | Transaction value in ₹ |
| `hour` | Hour of transaction (0–23) |
| `day_of_week` | Day (0=Monday … 6=Sunday) |
| `location_risk` | 1 if location is Unknown/International |
| `device_risk` | 1 if device is Unknown/New |
| `is_foreign` | 1 if international transaction |
| `velocity_score` | Approximation of transaction frequency |
| `log_amount` | log(1 + amount) — reduces skew |
| `odd_hour` | 1 if transaction between midnight and 5 AM |
| `composite_risk` | Sum of individual risk flags |

---

## 🔒 Security Features

- **Password hashing** — bcrypt with random salt (no plain-text passwords stored)
- **SQL injection prevention** — all queries use parameterised placeholders (`%s`)
- **Session-based auth** — Flask server-side sessions (not JWT, so no token theft)
- **Input validation** — both client-side (JS) and server-side (Python)
- **CORS** — configured with `flask-cors`

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside venv |
| `mysql.connector.errors.DatabaseError` | Check XAMPP MySQL is running; verify DB_CONFIG credentials |
| `FileNotFoundError: fraud_model.pkl` | Run `python ml/train_model.py` first |
| Port 5000 in use | Change `app.run(port=5001)` in `app.py` |
| Session not persisting in Postman | Enable "Automatically follow redirects" and cookie jar in Postman |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js v4 |
| Backend | Python 3.10+, Flask 3.0 |
| Database | MySQL 8 (via XAMPP) |
| ML Model | Scikit-learn Random Forest |
| Auth | bcrypt + Flask sessions |
| Testing | Pytest + Postman |

---

*Built for educational purposes. For production use, add HTTPS, rate limiting, and a proper secrets manager.*
