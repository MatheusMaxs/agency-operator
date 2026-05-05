import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from app.actions import log_agent_action
from app.db import get_conn
from app.safety import SafetyError, assert_approved_if_required, assert_business_can_be_contacted
from app.settings import settings
from app.site_builder import build_site


ToolFn = Callable[[dict[str, Any]], dict[str, Any]]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "business"


def dedupe_key(name: str, city: str, country: str) -> str:
    raw = f"{name}|{city}|{country}".lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def now() -> datetime:
    return datetime.now(timezone.utc)


def get_business(business_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM businesses WHERE id=%s", (business_id,)).fetchone()
    if not row:
        raise ValueError("Business not found")
    return dict(row)


def discover_businesses(payload: dict[str, Any]) -> dict[str, Any]:
    country = str(payload.get("country") or "Portugal")
    city = str(payload.get("city") or "Porto")
    limit = min(int(payload.get("limit") or 10), 50)
    categories = [
        "Restaurant",
        "Dental clinic",
        "Hair salon",
        "Bakery",
        "Physiotherapy clinic",
        "Boutique hotel",
        "Local tour operator",
        "Auto repair shop",
        "Coffee shop",
        "Yoga studio",
    ]

    created: list[dict[str, Any]] = []
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO cities(country, city) VALUES(%s,%s) ON CONFLICT DO NOTHING",
            (country, city),
        )
        for idx in range(limit):
            category = categories[idx % len(categories)]
            name = f"{city} {category} Concept {idx + 1}"
            key = dedupe_key(name, city, country)
            email = f"hello+demo-{slugify(name)}@example.com"
            row = conn.execute(
                """
                INSERT INTO businesses (
                  name, category, city, country, email, source_url, lead_state, dedupe_key, rating, review_count
                ) VALUES (%s,%s,%s,%s,%s,%s,'DISCOVERED',%s,%s,%s)
                ON CONFLICT (dedupe_key) DO UPDATE SET updated_at=now()
                RETURNING id, name, category, city, country, email, lead_state
                """,
                (
                    name,
                    category,
                    city,
                    country,
                    email,
                    f"manual-seed://{slugify(country)}/{slugify(city)}/{idx + 1}",
                    key,
                    4.0 + ((idx % 9) / 10),
                    8 + idx * 3,
                ),
            ).fetchone()
            created.append(dict(row))

    return {"created_or_seen": len(created), "businesses": created}


def audit_business(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = int(payload["business_id"])
    business = get_business(business_id)
    website = business.get("website")

    if not website:
        audit_score = 15
        problems = ["No website found", "Customers may rely only on social/profile pages", "No owned conversion path"]
        recommendations = ["Create a simple mobile-first website", "Add clear CTA", "Add contact and location details"]
        state = "HAS_NO_SITE"
    else:
        audit_score = 52
        problems = ["Website needs manual visual review", "CTA and mobile quality need verification"]
        recommendations = ["Improve above-the-fold clarity", "Check speed, SSL, SEO metadata, and forms"]
        state = "HAS_BAD_SITE"

    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO website_audits (
              business_id, website_url, audit_score, mobile_score, speed_score, visual_score,
              cta_score, seo_score, has_ssl, problems, recommendations
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
            RETURNING id, audit_score, problems, recommendations
            """,
            (
                business_id,
                website,
                audit_score,
                45 if website else 0,
                50 if website else 0,
                45 if website else 0,
                35 if website else 0,
                45 if website else 0,
                website.startswith("https://") if website else False,
                json.dumps(problems),
                json.dumps(recommendations),
            ),
        ).fetchone()
        conn.execute("UPDATE businesses SET lead_state=%s, updated_at=now() WHERE id=%s", (state, business_id))

    return {"business_id": business_id, "audit": dict(row), "lead_state": state}


def score_lead(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = int(payload["business_id"])
    business = get_business(business_id)
    with get_conn() as conn:
        audit = conn.execute(
            """
            SELECT * FROM website_audits
            WHERE business_id=%s
            ORDER BY id DESC
            LIMIT 1
            """,
            (business_id,),
        ).fetchone()

    has_email = bool(business.get("email"))
    has_phone = bool(business.get("phone"))
    has_website = bool(business.get("website"))
    review_count = int(business.get("review_count") or 0)

    need_score = 35 if not has_website else max(0, 80 - int(audit["audit_score"] if audit else 50))
    contactability_score = (15 if has_email else 0) + (10 if has_phone else 0)
    business_value_score = min(25, 8 + review_count // 4)
    complexity_score = 5 if business.get("category") in {"Restaurant", "Hair salon", "Bakery", "Coffee shop"} else 10
    opportunity_score = max(0, min(100, need_score + contactability_score + business_value_score - complexity_score))

    reasons = []
    if not has_website:
        reasons.append("No website detected")
    if has_email:
        reasons.append("Public email available")
    if review_count > 10:
        reasons.append("Business appears active")

    state = "QUALIFIED" if opportunity_score >= 55 else "ENRICHED"
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO lead_scores (
              business_id, need_score, contactability_score, business_value_score,
              complexity_score, opportunity_score, reasons
            ) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
            RETURNING *
            """,
            (
                business_id,
                need_score,
                contactability_score,
                business_value_score,
                complexity_score,
                opportunity_score,
                json.dumps(reasons),
            ),
        ).fetchone()
        conn.execute("UPDATE businesses SET lead_state=%s, updated_at=now() WHERE id=%s", (state, business_id))

    return {"business_id": business_id, "lead_score": dict(row), "lead_state": state}


def generate_site(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = int(payload["business_id"])
    business = get_business(business_id)
    html, css, brief = build_site(business)
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO generated_sites (business_id, status, site_type, title, brief, html, css, quality_score)
            VALUES (%s,'GENERATED','landing_page',%s,%s::jsonb,%s,%s,%s)
            RETURNING id, status, title, quality_score
            """,
            (
                business_id,
                f"{business['name']} website preview",
                json.dumps(brief),
                html,
                css,
                72,
            ),
        ).fetchone()
        conn.execute("UPDATE businesses SET lead_state='SITE_GENERATED', updated_at=now() WHERE id=%s", (business_id,))

    return {"business_id": business_id, "site": dict(row)}


def deploy_site(payload: dict[str, Any]) -> dict[str, Any]:
    site_id = int(payload["site_id"])
    preview_url = f"{settings.base_public_url}/generated-sites/{site_id}/html"
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE generated_sites
            SET status='DEPLOYED', preview_url=%s, updated_at=now()
            WHERE id=%s
            RETURNING id, business_id, status, preview_url
            """,
            (preview_url, site_id),
        ).fetchone()
        if not row:
            raise ValueError("Site not found")
        conn.execute("UPDATE businesses SET lead_state='SITE_DEPLOYED', updated_at=now() WHERE id=%s", (row["business_id"],))
    return {"site": dict(row)}


def prepare_outreach(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = int(payload["business_id"])
    business = get_business(business_id)
    with get_conn() as conn:
        site = conn.execute(
            """
            SELECT * FROM generated_sites
            WHERE business_id=%s
            ORDER BY id DESC
            LIMIT 1
            """,
            (business_id,),
        ).fetchone()
    if not site:
        raise ValueError("No generated site found")

    preview_url = site.get("preview_url") or f"{settings.base_public_url}/generated-sites/{site['id']}/html"
    subject = f"Quick website idea for {business['name']}"
    body = f"""Hi {business['name']},

I found {business['name']} while looking at local businesses in {business.get('city') or 'your area'}.

I noticed there may be room for a clearer web presence, so I built a small preview concept here:
{preview_url}

This is an automated but human-reviewable preview from {settings.brand_name}. I do not pretend this message is handwritten.

If you like it, I can customize and publish a simple mobile-ready site from 100-300 EUR depending on scope.

If this is not relevant, reply "no thanks" and I will not contact you again.

Thanks,
{settings.brand_name}
"""

    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO outreach_messages (business_id, generated_site_id, to_address, subject, body, status)
            VALUES (%s,%s,%s,%s,%s,'PREPARED')
            RETURNING id, business_id, to_address, subject, status
            """,
            (business_id, site["id"], business.get("email"), subject, body),
        ).fetchone()
        conn.execute("UPDATE businesses SET lead_state='CONTACT_READY', updated_at=now() WHERE id=%s", (business_id,))
    return {"message": dict(row), "body": body}


def send_outreach(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = int(payload["business_id"])
    assert_business_can_be_contacted(business_id)

    with get_conn() as conn:
        message = conn.execute(
            """
            SELECT * FROM outreach_messages
            WHERE business_id=%s AND status='PREPARED'
            ORDER BY id DESC
            LIMIT 1
            """,
            (business_id,),
        ).fetchone()
    if not message:
        raise ValueError("No prepared outreach message found")

    assert_approved_if_required("outreach_message", int(message["id"]), "SEND_OUTREACH")

    if settings.email_dry_run:
        with get_conn() as conn:
            row = conn.execute(
                """
                UPDATE outreach_messages SET status='DRY_RUN_SENT', sent_at=now()
                WHERE id=%s
                RETURNING id, status, sent_at
                """,
                (message["id"],),
            ).fetchone()
            conn.execute("UPDATE businesses SET lead_state='CONTACTED', updated_at=now() WHERE id=%s", (business_id,))
        return {"dry_run": True, "message": dict(row)}

    if not settings.resend_api_key:
        raise SafetyError("RESEND_API_KEY missing and EMAIL_DRY_RUN=false")

    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": settings.from_email,
            "to": [message["to_address"]],
            "subject": message["subject"],
            "text": message["body"],
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE outreach_messages
            SET status='SENT', sent_at=now(), provider_message_id=%s
            WHERE id=%s
            RETURNING id, status, sent_at, provider_message_id
            """,
            (data.get("id"), message["id"]),
        ).fetchone()
        conn.execute("UPDATE businesses SET lead_state='CONTACTED', updated_at=now() WHERE id=%s", (business_id,))
    return {"dry_run": False, "message": dict(row)}


def get_new_replies(payload: dict[str, Any]) -> dict[str, Any]:
    return {"replies": [], "note": "Connect inbound email webhooks before enabling automated replies."}


def get_daily_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
              (SELECT count(*) FROM businesses) AS businesses,
              (SELECT count(*) FROM businesses WHERE lead_state='QUALIFIED') AS qualified,
              (SELECT count(*) FROM generated_sites) AS sites,
              (SELECT count(*) FROM outreach_messages WHERE status IN ('SENT','DRY_RUN_SENT')) AS contacts_sent,
              (SELECT coalesce(sum(amount),0) FROM payments WHERE payment_status='PAID') AS revenue_cents,
              (SELECT count(*) FROM approvals WHERE status='PENDING') AS approvals_pending,
              (SELECT count(*) FROM agent_actions) AS actions
            """
        ).fetchone()
    metrics = dict(row)
    metrics["revenue_eur"] = float(metrics.pop("revenue_cents") or 0) / 100
    return metrics


TOOLS: dict[str, ToolFn] = {
    "discover_businesses": discover_businesses,
    "audit_business": audit_business,
    "score_lead": score_lead,
    "generate_site": generate_site,
    "deploy_site": deploy_site,
    "prepare_outreach": prepare_outreach,
    "send_outreach": send_outreach,
    "get_new_replies": get_new_replies,
    "get_daily_metrics": get_daily_metrics,
}


def call_tool(tool_name: str, payload: dict[str, Any], agent_name: str = "system") -> dict[str, Any]:
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    started_at = now()
    try:
        output = TOOLS[tool_name](payload)
        log_agent_action(
            agent_name=agent_name,
            action_type=tool_name,
            status="completed",
            target_type=payload.get("target_type"),
            target_id=str(payload.get("business_id") or payload.get("site_id") or "") or None,
            input_json=payload,
            output_json=output,
            started_at=started_at,
            finished_at=now(),
        )
        return output
    except Exception as exc:
        log_agent_action(
            agent_name=agent_name,
            action_type=tool_name,
            status="failed",
            input_json=payload,
            output_json={},
            error_message=str(exc),
            started_at=started_at,
            finished_at=now(),
        )
        raise
