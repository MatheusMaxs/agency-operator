CREATE TABLE IF NOT EXISTS cities (
  id BIGSERIAL PRIMARY KEY,
  country TEXT NOT NULL,
  city TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT true,
  priority INTEGER NOT NULL DEFAULT 50,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(country, city)
);

CREATE TABLE IF NOT EXISTS businesses (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  city TEXT,
  country TEXT,
  address TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,
  instagram_url TEXT,
  facebook_url TEXT,
  linkedin_url TEXT,
  google_maps_url TEXT,
  source_url TEXT,
  opening_hours JSONB NOT NULL DEFAULT '{}',
  rating NUMERIC(3,2),
  review_count INTEGER,
  lead_state TEXT NOT NULL DEFAULT 'DISCOVERED',
  dedupe_key TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS businesses_dedupe_idx
ON businesses (dedupe_key)
WHERE dedupe_key IS NOT NULL;

CREATE TABLE IF NOT EXISTS business_contacts (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  contact_type TEXT NOT NULL,
  value TEXT NOT NULL,
  source_url TEXT,
  verified BOOLEAN NOT NULL DEFAULT false,
  do_not_contact BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(business_id, contact_type, value)
);

CREATE TABLE IF NOT EXISTS website_audits (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  website_url TEXT,
  audit_score INTEGER NOT NULL DEFAULT 0,
  mobile_score INTEGER,
  speed_score INTEGER,
  visual_score INTEGER,
  cta_score INTEGER,
  seo_score INTEGER,
  has_ssl BOOLEAN,
  problems JSONB NOT NULL DEFAULT '[]',
  recommendations JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lead_scores (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  need_score INTEGER NOT NULL DEFAULT 0,
  contactability_score INTEGER NOT NULL DEFAULT 0,
  business_value_score INTEGER NOT NULL DEFAULT 0,
  complexity_score INTEGER NOT NULL DEFAULT 0,
  opportunity_score INTEGER NOT NULL DEFAULT 0,
  reasons JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS design_references (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT REFERENCES businesses(id) ON DELETE SET NULL,
  source_url TEXT,
  source_type TEXT,
  extracted_patterns JSONB NOT NULL DEFAULT '{}',
  design_brief JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS generated_sites (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'DRAFT',
  site_type TEXT NOT NULL DEFAULT 'landing_page',
  title TEXT,
  brief JSONB NOT NULL DEFAULT '{}',
  html TEXT NOT NULL DEFAULT '',
  css TEXT NOT NULL DEFAULT '',
  preview_url TEXT,
  desktop_screenshot_url TEXT,
  mobile_screenshot_url TEXT,
  quality_score INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS site_versions (
  id BIGSERIAL PRIMARY KEY,
  site_id BIGINT NOT NULL REFERENCES generated_sites(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  html TEXT NOT NULL,
  css TEXT NOT NULL DEFAULT '',
  change_note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(site_id, version_number)
);

CREATE TABLE IF NOT EXISTS outreach_messages (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  generated_site_id BIGINT REFERENCES generated_sites(id) ON DELETE SET NULL,
  channel TEXT NOT NULL DEFAULT 'email',
  to_address TEXT,
  subject TEXT,
  body TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'PREPARED',
  provider_message_id TEXT,
  approved_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  opened_at TIMESTAMPTZ,
  clicked_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS conversations (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  channel TEXT NOT NULL DEFAULT 'email',
  status TEXT NOT NULL DEFAULT 'OPEN',
  last_message_at TIMESTAMPTZ,
  summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payments (
  id BIGSERIAL PRIMARY KEY,
  business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  package_name TEXT NOT NULL,
  stripe_customer_id TEXT,
  checkout_session_id TEXT,
  payment_status TEXT NOT NULL DEFAULT 'PENDING',
  amount INTEGER NOT NULL,
  currency TEXT NOT NULL DEFAULT 'eur',
  invoice_url TEXT,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id BIGSERIAL PRIMARY KEY,
  approval_type TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id BIGINT NOT NULL,
  status TEXT NOT NULL DEFAULT 'PENDING',
  reason TEXT,
  requested_by TEXT NOT NULL DEFAULT 'system',
  approved_by TEXT,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(approval_type, target_type, target_id)
);

CREATE TABLE IF NOT EXISTS agent_actions (
  id BIGSERIAL PRIMARY KEY,
  agent_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  target_type TEXT,
  target_id TEXT,
  status TEXT NOT NULL,
  input_json JSONB NOT NULL DEFAULT '{}',
  output_json JSONB NOT NULL DEFAULT '{}',
  error_message TEXT,
  model_used TEXT,
  tokens_input INTEGER NOT NULL DEFAULT 0,
  tokens_output INTEGER NOT NULL DEFAULT 0,
  estimated_cost_eur NUMERIC(12,6) NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS llm_usage (
  id BIGSERIAL PRIMARY KEY,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  task_type TEXT,
  business_id BIGINT REFERENCES businesses(id) ON DELETE SET NULL,
  tokens_input INTEGER NOT NULL DEFAULT 0,
  tokens_output INTEGER NOT NULL DEFAULT 0,
  cached_tokens INTEGER NOT NULL DEFAULT 0,
  estimated_cost_eur NUMERIC(12,6) NOT NULL DEFAULT 0,
  success BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS daily_metrics (
  id BIGSERIAL PRIMARY KEY,
  metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
  revenue_eur NUMERIC(12,2) NOT NULL DEFAULT 0,
  cost_eur NUMERIC(12,2) NOT NULL DEFAULT 0,
  leads_scraped INTEGER NOT NULL DEFAULT 0,
  qualified_leads INTEGER NOT NULL DEFAULT 0,
  sites_generated INTEGER NOT NULL DEFAULT 0,
  contacts_sent INTEGER NOT NULL DEFAULT 0,
  replies INTEGER NOT NULL DEFAULT 0,
  paid_customers INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(metric_date)
);

CREATE TABLE IF NOT EXISTS system_costs (
  id BIGSERIAL PRIMARY KEY,
  cost_type TEXT NOT NULL,
  amount_eur NUMERIC(12,6) NOT NULL,
  description TEXT,
  business_id BIGINT REFERENCES businesses(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
