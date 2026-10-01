-- Pro Studio initial schema (applied 2026-10-01 via wrangler d1 execute --remote)
CREATE TABLE IF NOT EXISTS contractors (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  company TEXT NOT NULL,
  logo_url TEXT,
  license_no TEXT,
  phone TEXT,
  stripe_customer_id TEXT,
  plan_tier TEXT DEFAULT 'payg',
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS plans (
  id TEXT PRIMARY KEY,
  contractor_id TEXT NOT NULL REFERENCES contractors(id),
  client_name TEXT,
  address TEXT,
  county TEXT NOT NULL,
  plan_type TEXT NOT NULL,
  dimensions TEXT,
  exposure TEXT,
  base_pdf TEXT NOT NULL,
  pdf_key TEXT,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS usage_events (
  id TEXT PRIMARY KEY,
  contractor_id TEXT NOT NULL REFERENCES contractors(id),
  plan_id TEXT REFERENCES plans(id),
  billed INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_otps (
  email TEXT PRIMARY KEY,
  code_hash TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  attempts INTEGER DEFAULT 0
);
