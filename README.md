# 🔐 AI-Based Banking Security System

## 📌 Overview

This project is a Flask-based web application designed to detect fraudulent banking transactions using Machine Learning. It enhances security with OTP-based Multi-Factor Authentication (MFA) and real-time risk analysis.

---

## 🚀 Features

* 🔐 Secure Login System (bcrypt hashing)
* 📩 OTP-based Authentication (MFA)
* 🤖 Fraud Detection using Machine Learning
* 📊 Risk Classification (LOW, MEDIUM, HIGH)
* 🧠 Real-time Risk Analysis
* 🗄 MySQL Database Integration
* 📜 Threat Logging System

---

## 🛠 Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, JavaScript
* **Database:** MySQL
* **Machine Learning:** Scikit-learn
* **Authentication:** Bcrypt + OTP (Email)

---

## ⚙️ How to Run

1️⃣ Clone the repository:

```
git clone https://github.com/Harishkuyate/banking-security-ai.git
```

2️⃣ Navigate to project folder:

```
cd banking-security-ai
```

3️⃣ Install dependencies:

```
pip install -r requirements.txt
```

4️⃣ Setup MySQL database:

* Create database: `banking_security`
* Run: `database/setup.sql`

5️⃣ Run the application:

```
python app.py
```

6️⃣ Open in browser:

```
http://localhost:5001
```

---

## 🧪 Testing

* API testing using Postman (included in `/tests`)
* Unit testing available in `tests/test_app.py`

---

## 🔍 Risk Calculation Logic

Risk is calculated using:

* Transaction amount
* Location risk (foreign/unknown)
* Device risk (new/unknown device)
* Time (odd hours)
* ML model probability

Final output:

* LOW (<30%)
* MEDIUM (30–65%)
* HIGH (>65%)

---

## 🛡 Software Quality Assurance (SQA)

* Input Validation & Error Handling
* Secure Authentication (bcrypt + MFA)
* Session Management
* Logging & Monitoring (threat_logs)
* Unit Testing
* Secure Coding Practices

---

## 📸 Screenshots

(Add your project screenshots here)

---

## 👨‍💻 Author

**Harish Kuyate**

---

## ⭐ Future Improvements

* SMS OTP Integration
* Advanced ML Model
* Real-time alerts
* Admin dashboard

---
