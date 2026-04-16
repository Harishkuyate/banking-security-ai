"""
=============================================================
  SecureBank AI — Unit & Integration Tests
  File: tests/test_app.py
  Run:  python -m pytest tests/test_app.py -v
=============================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json


# ── Fixtures ─────────────────────────────────────────────────
@pytest.fixture
def client():
    """Create a Flask test client."""
    from app import app
    app.config["TESTING"]    = True
    app.config["SECRET_KEY"] = "test_secret"
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    """Register + login a test user, return authenticated client."""
    client.post("/api/register", json={
        "name"    : "Test User",
        "email"   : "pytest@example.com",
        "password": "Test@1234"
    })
    client.post("/api/login", json={
        "email"   : "pytest@example.com",
        "password": "Test@1234"
    })
    return client


# ── Health Check ─────────────────────────────────────────────
class TestHealth:
    def test_health_endpoint_returns_200(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200

    def test_health_response_has_status(self, client):
        data = res = client.get("/api/health").get_json()
        assert data["status"] == "ok"


# ── Registration ─────────────────────────────────────────────
class TestRegistration:
    def test_register_success(self, client):
        res = client.post("/api/register", json={
            "name": "Alice", "email": "alice_test@x.com", "password": "Pass123"
        })
        assert res.status_code == 201
        assert "user_id" in res.get_json()

    def test_register_missing_fields(self, client):
        res = client.post("/api/register", json={"email": "x@x.com"})
        assert res.status_code == 400

    def test_register_invalid_email(self, client):
        res = client.post("/api/register", json={
            "name": "Bob", "email": "not-an-email", "password": "Pass123"
        })
        assert res.status_code == 400

    def test_register_short_password(self, client):
        res = client.post("/api/register", json={
            "name": "Bob", "email": "bob2@x.com", "password": "ab"
        })
        assert res.status_code == 400

    def test_register_duplicate_email(self, client):
        data = {"name": "X", "email": "dup@x.com", "password": "Pass123"}
        client.post("/api/register", json=data)
        res = client.post("/api/register", json=data)
        assert res.status_code == 409


# ── Login ─────────────────────────────────────────────────────
class TestLogin:
    def test_login_success(self, client):
        client.post("/api/register", json={
            "name": "Login User", "email": "login@x.com", "password": "Pass123"
        })
        res = client.post("/api/login", json={
            "email": "login@x.com", "password": "Pass123"
        })
        assert res.status_code == 200
        assert "user" in res.get_json()

    def test_login_wrong_password(self, client):
        client.post("/api/register", json={
            "name": "U", "email": "wrong_pw@x.com", "password": "Correct1"
        })
        res = client.post("/api/login", json={
            "email": "wrong_pw@x.com", "password": "WrongPass"
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/login", json={
            "email": "nobody@x.com", "password": "anything"
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/login", json={"email": "x@x.com"})
        assert res.status_code == 400


# ── Auth Guard ────────────────────────────────────────────────
class TestAuthGuard:
    def test_me_unauthenticated(self, client):
        res = client.get("/api/me")
        assert res.status_code == 401

    def test_transactions_unauthenticated(self, client):
        res = client.get("/api/transactions")
        assert res.status_code == 401

    def test_dashboard_unauthenticated(self, client):
        res = client.get("/api/dashboard/stats")
        assert res.status_code == 401


# ── Transactions ──────────────────────────────────────────────
class TestTransactions:
    def test_add_transaction_valid(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount"     : 500,
            "location"   : "Mumbai",
            "device_info": "Personal Laptop",
            "is_foreign" : 0
        })
        assert res.status_code == 201
        data = res.get_json()
        assert "transaction_id" in data
        assert "risk_level"     in data
        assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_add_transaction_high_risk(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount"     : 15000,
            "location"   : "Unknown",
            "device_info": "Unknown",
            "is_foreign" : 1
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data["risk_level"] in ("MEDIUM", "HIGH")

    def test_add_transaction_negative_amount(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount": -100, "location": "Mumbai",
            "device_info": "Laptop", "is_foreign": 0
        })
        assert res.status_code == 400

    def test_add_transaction_zero_amount(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount": 0, "location": "Delhi",
            "device_info": "Mobile", "is_foreign": 0
        })
        assert res.status_code == 400

    def test_add_transaction_exceeds_limit(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount": 2_000_000, "location": "Mumbai",
            "device_info": "Laptop", "is_foreign": 0
        })
        assert res.status_code == 400

    def test_get_transactions_returns_list(self, auth_client):
        res = auth_client.get("/api/transactions")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_transaction_response_fields(self, auth_client):
        res = auth_client.post("/api/transactions", json={
            "amount": 200, "location": "Pune",
            "device_info": "Personal Mobile", "is_foreign": 0
        })
        data = res.get_json()
        for field in ("transaction_id", "amount", "status", "risk_level", "fraud_probability"):
            assert field in data, f"Missing field: {field}"

    def test_fraud_probability_range(self, auth_client):
        res  = auth_client.post("/api/transactions", json={
            "amount": 300, "location": "Bengaluru",
            "device_info": "Personal Laptop", "is_foreign": 0
        })
        prob = res.get_json()["fraud_probability"]
        assert 0 <= prob <= 100


# ── Dashboard ─────────────────────────────────────────────────
class TestDashboard:
    def test_dashboard_stats_structure(self, auth_client):
        res  = auth_client.get("/api/dashboard/stats")
        assert res.status_code == 200
        data = res.get_json()
        for key in ("total_transactions", "total_amount", "normal_count",
                    "suspicious_count", "risk_breakdown", "recent_transactions"):
            assert key in data, f"Missing key: {key}"

    def test_risk_breakdown_keys(self, auth_client):
        data = auth_client.get("/api/dashboard/stats").get_json()
        rb   = data["risk_breakdown"]
        for k in ("LOW", "MEDIUM", "HIGH"):
            assert k in rb


# ── Threat Logs ───────────────────────────────────────────────
class TestThreatLogs:
    def test_get_threat_logs(self, auth_client):
        res = auth_client.get("/api/threat-logs")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)


# ── Logout ────────────────────────────────────────────────────
class TestLogout:
    def test_logout_success(self, auth_client):
        res = auth_client.post("/api/logout")
        assert res.status_code == 200

    def test_protected_after_logout(self, auth_client):
        auth_client.post("/api/logout")
        res = auth_client.get("/api/me")
        assert res.status_code == 401


# ── ML Model Helper ───────────────────────────────────────────
class TestRiskLevel:
    def test_risk_level_low(self):
        from app import get_risk_level
        assert get_risk_level(0.1)  == "LOW"
        assert get_risk_level(0.29) == "LOW"

    def test_risk_level_medium(self):
        from app import get_risk_level
        assert get_risk_level(0.30) == "MEDIUM"
        assert get_risk_level(0.64) == "MEDIUM"

    def test_risk_level_high(self):
        from app import get_risk_level
        assert get_risk_level(0.65) == "HIGH"
        assert get_risk_level(0.99) == "HIGH"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
