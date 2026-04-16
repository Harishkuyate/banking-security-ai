-- =============================================================
--  AI Banking Security System - Database Setup
--  File: database/setup.sql
--  Usage: Run this in phpMyAdmin or MySQL CLI
--    mysql -u root -p < database/setup.sql
-- =============================================================

-- Create and select the database
CREATE DATABASE IF NOT EXISTS banking_security
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE banking_security;

-- ─── Table: users ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id         INT          AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,        -- bcrypt hash
  created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email)
) ENGINE=InnoDB;

-- ─── Table: transactions ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
  id                 INT            AUTO_INCREMENT PRIMARY KEY,
  user_id            INT            NOT NULL,
  amount             DECIMAL(12, 2) NOT NULL,
  location           VARCHAR(150)   DEFAULT 'Unknown',
  device_info        VARCHAR(150)   DEFAULT 'Unknown',
  is_foreign         TINYINT(1)     DEFAULT 0,
  status             ENUM('NORMAL','SUSPICIOUS') DEFAULT 'NORMAL',
  fraud_probability  FLOAT          DEFAULT 0.0,
  risk_level         ENUM('LOW','MEDIUM','HIGH')  DEFAULT 'LOW',
  created_at         DATETIME       DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user    (user_id),
  INDEX idx_status  (status),
  INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- ─── Table: threat_logs ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS threat_logs (
  id                INT     AUTO_INCREMENT PRIMARY KEY,
  transaction_id    INT     NOT NULL,
  risk_level        ENUM('LOW','MEDIUM','HIGH') DEFAULT 'LOW',
  fraud_probability FLOAT   DEFAULT 0.0,
  location_risk     TINYINT DEFAULT 0,
  device_risk       TINYINT DEFAULT 0,
  is_foreign        TINYINT DEFAULT 0,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
  INDEX idx_transaction (transaction_id),
  INDEX idx_risk        (risk_level)
) ENGINE=InnoDB;

-- ─── Sample seed data (optional) ─────────────────────────────
-- Password for both accounts is: Test@1234
-- (bcrypt hash generated with Python: bcrypt.hashpw(b"Test@1234", bcrypt.gensalt()))
-- Replace the hash below with a freshly generated one if needed.

-- INSERT INTO users (name, email, password) VALUES
--   ('Alice Demo', 'alice@example.com', '$2b$12$REPLACE_WITH_REAL_HASH'),
--   ('Bob Demo',   'bob@example.com',   '$2b$12$REPLACE_WITH_REAL_HASH');

-- Verify structure
SHOW TABLES;
DESCRIBE users;
DESCRIBE transactions;
DESCRIBE threat_logs;
