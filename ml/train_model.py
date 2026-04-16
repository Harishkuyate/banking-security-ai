"""
=============================================================
  AI-Based Security Threat Detection - Model Training Script
  File: ml/train_model.py
  Description: Trains a Random Forest classifier to detect
               fraudulent banking transactions.
=============================================================
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, roc_auc_score)
import joblib
import os
import json

# ─── Configuration ───────────────────────────────────────────
MODEL_DIR   = os.path.dirname(os.path.abspath(__file__))
DATASET     = os.path.join(MODEL_DIR, "transactions_dataset.csv")
MODEL_PATH  = os.path.join(MODEL_DIR, "fraud_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
META_PATH   = os.path.join(MODEL_DIR, "model_meta.json")

FEATURE_COLS = [
    "amount", "hour", "day_of_week",
    "location_risk", "device_risk",
    "is_foreign", "velocity_score"
]
TARGET_COL = "is_fraud"


# ─── 1. Load & Inspect Data ──────────────────────────────────
def load_data():
    print("📂 Loading dataset...")
    df = pd.read_csv(DATASET)
    print(f"   Rows: {len(df)} | Columns: {list(df.columns)}")
    print(f"   Fraud rate: {df[TARGET_COL].mean()*100:.1f}%\n")
    return df


# ─── 2. Feature Engineering ──────────────────────────────────
def engineer_features(df):
    """Add derived features that improve fraud detection."""
    df = df.copy()

    # Amount buckets (log-scale normalization helps tree models too)
    df["log_amount"] = np.log1p(df["amount"])

    # Is the transaction at an odd hour (midnight–5am)?
    df["odd_hour"] = ((df["hour"] >= 0) & (df["hour"] <= 5)).astype(int)

    # Composite risk score
    df["composite_risk"] = (
        df["location_risk"] + df["device_risk"] +
        df["is_foreign"] + df["odd_hour"]
    )

    return df


# ─── 3. Train/Test Split ─────────────────────────────────────
def split_data(df):
    extended_features = FEATURE_COLS + ["log_amount", "odd_hour", "composite_risk"]
    X = df[extended_features]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"📊 Train size: {len(X_train)} | Test size: {len(X_test)}\n")
    return X_train, X_test, y_train, y_test, extended_features


# ─── 4. Scale Features ───────────────────────────────────────
def scale_features(X_train, X_test):
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)
    return X_train_sc, X_test_sc, scaler


# ─── 5. Train Model ──────────────────────────────────────────
def train_model(X_train, y_train):
    print("🤖 Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",   # handles class imbalance
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("   Training complete!\n")
    return model


# ─── 6. Evaluate Model ───────────────────────────────────────
def evaluate_model(model, X_test, y_test, feature_names):
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print("═" * 50)
    print("  MODEL EVALUATION RESULTS")
    print("═" * 50)
    print(f"  Accuracy : {acc*100:.2f}%")
    print(f"  ROC-AUC  : {auc:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred,
                                target_names=["Normal", "Fraud"]))
    print("  Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("═" * 50)

    # Feature importances
    importances = dict(zip(feature_names, model.feature_importances_))
    print("\n  Top Feature Importances:")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 40)
        print(f"  {feat:<20} {imp:.4f}  {bar}")

    return acc, auc, importances


# ─── 7. Save Artifacts ───────────────────────────────────────
def save_artifacts(model, scaler, feature_names, acc, auc):
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    meta = {
        "features": feature_names,
        "accuracy": round(acc, 4),
        "roc_auc" : round(auc, 4),
        "classes" : ["Normal", "Fraud"]
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n✅ Model saved  → {MODEL_PATH}")
    print(f"✅ Scaler saved → {SCALER_PATH}")
    print(f"✅ Meta saved   → {META_PATH}\n")


# ─── 8. Risk Level Helper ────────────────────────────────────
def get_risk_level(fraud_probability: float) -> str:
    """Map fraud probability to human-readable risk level."""
    if fraud_probability < 0.3:
        return "LOW"
    elif fraud_probability < 0.65:
        return "MEDIUM"
    else:
        return "HIGH"


# ─── Main ────────────────────────────────────────────────────
if __name__ == "__main__":
    df               = load_data()
    df               = engineer_features(df)
    X_tr, X_te, y_tr, y_te, feats = split_data(df)
    X_tr_sc, X_te_sc, scaler      = scale_features(X_tr, X_te)
    model                         = train_model(X_tr_sc, y_tr)
    acc, auc, _                   = evaluate_model(model, X_te_sc, y_te, feats)
    save_artifacts(model, scaler, feats, acc, auc)

    # Quick sanity check
    print("🔬 Quick Prediction Test:")
    sample_normal = [[120.50, 14, 2, 0, 0, 0, 1, np.log1p(120.50), 0, 0]]
    sample_fraud  = [[15000.0, 3, 1, 1, 1, 1, 9, np.log1p(15000.0), 1, 4]]
    for label, sample in [("Normal", sample_normal), ("Fraud", sample_fraud)]:
        sc_sample = scaler.transform(sample)
        prob = model.predict_proba(sc_sample)[0][1]
        risk = get_risk_level(prob)
        print(f"   {label:6s} txn → Fraud prob: {prob:.2%} → Risk: {risk}")
