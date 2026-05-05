# First Run

## 1. Start Services

```bash
cd /opt/agency-operator
cp .env.example .env
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/health
```

## 2. Create Demo Leads

```bash
curl -X POST http://127.0.0.1:8000/tools/discover_businesses \
  -H "Content-Type: application/json" \
  -d '{"country":"Portugal","city":"Porto","limit":5}'
```

## 3. Run One Full Lead Flow

Replace `1` with a real business ID from `/businesses`.

```bash
curl http://127.0.0.1:8000/businesses

curl -X POST http://127.0.0.1:8000/tools/audit_business \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'

curl -X POST http://127.0.0.1:8000/tools/score_lead \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'

curl -X POST http://127.0.0.1:8000/tools/generate_site \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'
```

Get site ID:

```bash
curl http://127.0.0.1:8000/generated-sites
```

Deploy preview:

```bash
curl -X POST http://127.0.0.1:8000/tools/deploy_site \
  -H "Content-Type: application/json" \
  -d '{"site_id":1}'
```

Prepare outreach:

```bash
curl -X POST http://127.0.0.1:8000/tools/prepare_outreach \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'
```

Try send. This should request approval first:

```bash
curl -X POST http://127.0.0.1:8000/tools/send_outreach \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'
```

Approve in dashboard or API:

```bash
curl http://127.0.0.1:8000/approvals
curl -X POST http://127.0.0.1:8000/approvals/1/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by":"owner"}'
```

Send again. With `EMAIL_DRY_RUN=true`, it logs a dry-run send only:

```bash
curl -X POST http://127.0.0.1:8000/tools/send_outreach \
  -H "Content-Type: application/json" \
  -d '{"business_id":1}'
```

Create a Kiwify payment link after clear interest:

```bash
curl -X POST http://127.0.0.1:8000/tools/create_payment_link \
  -H "Content-Type: application/json" \
  -d '{"business_id":1,"package_name":"LOCAL_BUSINESS_SITE"}'
```

Webhook endpoint for Kiwify payment events:

```text
https://YOUR_API_DOMAIN/webhooks/kiwify
```

## 4. Dashboard

From Windows, tunnel dashboard over Tailscale:

```powershell
ssh -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 root@100.117.195.39
```

Open:

```text
http://127.0.0.1:3000
```

## 5. MCP Bridge

Manifest:

```bash
curl http://127.0.0.1:8100/manifest
```

Call tool:

```bash
curl -X POST http://127.0.0.1:8100/call \
  -H "Content-Type: application/json" \
  -d '{"tool":"get_daily_metrics","arguments":{},"agent_name":"hermes"}'
```
