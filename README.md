# Agency Operator

Complete MVP starter for a 24/7 Hermes-powered web-agency operator.

This project gives you the base machine:

- PostgreSQL schema for leads, sites, messages, payments, costs, and `agent_actions`.
- FastAPI backend with logged business tools.
- Redis queue worker for slow jobs.
- MCP-style HTTP bridge that Hermes or another agent can call.
- Next.js dashboard for overview, leads, approvals, and actions.
- Safety gates: no duplicate outreach, do-not-contact protection, dry-run email by default, approval before first outreach.

It is intentionally an MVP. It does not scrape at scale, does not bypass platform limits, does not clone protected designs, and does not send real email until you configure a provider and disable dry-run.

## Quick Start On VPS

```bash
cd /opt
git clone YOUR_REPO_URL agency-operator
cd agency-operator
cp .env.example .env
docker compose up -d --build
curl http://127.0.0.1:8000/health
```

If you copied this folder manually instead of using git:

```bash
cd agency-operator
cp .env.example .env
docker compose up -d --build
```

Open dashboard through an SSH tunnel over Tailscale:

```powershell
ssh -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 root@100.117.195.39
```

Then open:

```text
http://127.0.0.1:3000
```

## First Test

Create demo businesses:

```bash
curl -X POST http://127.0.0.1:8000/tools/discover_businesses \
  -H "Content-Type: application/json" \
  -d '{"country":"Portugal","city":"Porto","limit":5}'
```

Generate an overview:

```bash
curl http://127.0.0.1:8000/metrics/overview
```

## Tool Flow

Recommended order:

1. `discover_businesses`
2. `audit_business`
3. `score_lead`
4. `generate_site`
5. `deploy_site`
6. `prepare_outreach`
7. `send_outreach`

`send_outreach` creates an approval request by default. You approve in the dashboard or API before a real send.

## Important Safety Notes

- Keep `EMAIL_DRY_RUN=true` until you are ready.
- Keep `OUTREACH_REQUIRES_APPROVAL=true` for the first campaigns.
- Do not contact businesses that opted out.
- Do not pretend to be human.
- If you are under 18, use a responsible adult/legal guardian for payments, contracts, and ownership.
