from typing import Any

from fastapi import Body, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from redis import Redis
from rq import Queue
from rq.job import Job

from app.db import get_conn, init_db
from app.payments import handle_kiwify_webhook
from app.settings import settings
from app.tools import TOOLS, call_tool


app = FastAPI(title="Agency Operator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def queue() -> Queue:
    return Queue("default", connection=Redis.from_url(settings.redis_url))


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "agency-operator-api",
        "tools": sorted(TOOLS.keys()),
        "email_dry_run": settings.email_dry_run,
        "outreach_requires_approval": settings.outreach_requires_approval,
        "payments_provider": "kiwify",
        "nvidia_configured": bool(settings.nvidia_api_key and settings.nvidia_text_model),
        "vercel_configured": bool(settings.vercel_token),
    }


@app.get("/tools")
def list_tools() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": name,
                "description": DESCRIPTION_BY_TOOL.get(name, "Business operation tool"),
            }
            for name in sorted(TOOLS.keys())
        ]
    }


@app.post("/tools/{tool_name}")
def run_tool(tool_name: str, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    try:
        return call_tool(tool_name, payload, agent_name=str(payload.get("agent_name") or "api"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tools/{tool_name}/enqueue")
def enqueue_tool(tool_name: str, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    if tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail="Unknown tool")
    job = queue().enqueue("app.tasks.run_tool_job", tool_name, payload, "worker")
    return {"job_id": job.id, "status": "queued", "tool_name": tool_name}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    try:
        job = Job.fetch(job_id, connection=Redis.from_url(settings.redis_url))
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {
        "id": job.id,
        "status": job.get_status(),
        "result": job.result,
        "exc_info": job.exc_info,
    }


@app.get("/businesses")
def list_businesses(limit: int = 100, state: str | None = None) -> list[dict[str, Any]]:
    limit = min(limit, 500)
    with get_conn() as conn:
        if state:
            rows = conn.execute(
                "SELECT * FROM businesses WHERE lead_state=%s ORDER BY id DESC LIMIT %s",
                (state, limit),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM businesses ORDER BY id DESC LIMIT %s", (limit,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/businesses/{business_id}")
def get_business_detail(business_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        business = conn.execute("SELECT * FROM businesses WHERE id=%s", (business_id,)).fetchone()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        audits = conn.execute(
            "SELECT * FROM website_audits WHERE business_id=%s ORDER BY id DESC LIMIT 10",
            (business_id,),
        ).fetchall()
        scores = conn.execute(
            "SELECT * FROM lead_scores WHERE business_id=%s ORDER BY id DESC LIMIT 10",
            (business_id,),
        ).fetchall()
        sites = conn.execute(
            "SELECT id, status, title, preview_url, quality_score, created_at FROM generated_sites WHERE business_id=%s ORDER BY id DESC",
            (business_id,),
        ).fetchall()
        messages = conn.execute(
            "SELECT * FROM outreach_messages WHERE business_id=%s ORDER BY id DESC",
            (business_id,),
        ).fetchall()
    return {
        "business": dict(business),
        "audits": [dict(row) for row in audits],
        "scores": [dict(row) for row in scores],
        "sites": [dict(row) for row in sites],
        "messages": [dict(row) for row in messages],
    }


@app.post("/businesses/{business_id}/do-not-contact")
def mark_do_not_contact(business_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE businesses SET lead_state='DO_NOT_CONTACT', updated_at=now()
            WHERE id=%s RETURNING id, lead_state
            """,
            (business_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Business not found")
        conn.execute(
            "UPDATE business_contacts SET do_not_contact=true WHERE business_id=%s",
            (business_id,),
        )
    return dict(row)


@app.get("/generated-sites/{site_id}/html", response_class=HTMLResponse)
def generated_site_html(site_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT html FROM generated_sites WHERE id=%s", (site_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Site not found")
    return row["html"]


@app.get("/generated-sites")
def list_generated_sites(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT gs.id, gs.business_id, b.name AS business_name, gs.status, gs.title,
                   gs.preview_url, gs.quality_score, gs.created_at
            FROM generated_sites gs
            JOIN businesses b ON b.id=gs.business_id
            ORDER BY gs.id DESC
            LIMIT %s
            """,
            (min(limit, 500),),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/outreach/messages")
def list_outreach_messages(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT om.*, b.name AS business_name
            FROM outreach_messages om
            JOIN businesses b ON b.id=om.business_id
            ORDER BY om.id DESC
            LIMIT %s
            """,
            (min(limit, 500),),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/payments")
def list_payments(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT p.*, b.name AS business_name
            FROM payments p
            JOIN businesses b ON b.id=p.business_id
            ORDER BY p.id DESC
            LIMIT %s
            """,
            (min(limit, 500),),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/subscriptions")
def list_subscriptions(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT s.*, b.name AS business_name
            FROM subscriptions s
            JOIN businesses b ON b.id=s.business_id
            ORDER BY s.id DESC
            LIMIT %s
            """,
            (min(limit, 500),),
        ).fetchall()
    return [dict(row) for row in rows]


@app.post("/webhooks/kiwify")
def kiwify_webhook(
    payload: dict[str, Any] = Body(default_factory=dict),
    x_agency_webhook_token: str | None = Header(default=None),
    x_kiwify_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    if settings.kiwify_webhook_token:
        bearer = f"Bearer {settings.kiwify_webhook_token}"
        provided = {x_agency_webhook_token, x_kiwify_token, authorization}
        if settings.kiwify_webhook_token not in provided and bearer not in provided:
            raise HTTPException(status_code=401, detail="Invalid Kiwify webhook token")
    try:
        return handle_kiwify_webhook(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/approvals")
def list_approvals(status: str | None = None) -> list[dict[str, Any]]:
    with get_conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM approvals WHERE status=%s ORDER BY id DESC LIMIT 200",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM approvals ORDER BY id DESC LIMIT 200").fetchall()
    return [dict(row) for row in rows]


@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    approved_by = str(payload.get("approved_by") or "owner")
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE approvals
            SET status='APPROVED', approved_by=%s, approved_at=now()
            WHERE id=%s
            RETURNING *
            """,
            (approved_by, approval_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Approval not found")
    return dict(row)


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    approved_by = str(payload.get("approved_by") or "owner")
    with get_conn() as conn:
        row = conn.execute(
            """
            UPDATE approvals
            SET status='REJECTED', approved_by=%s, approved_at=now()
            WHERE id=%s
            RETURNING *
            """,
            (approved_by, approval_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Approval not found")
    return dict(row)


@app.get("/agent-actions")
def list_agent_actions(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, agent_name, action_type, target_type, target_id, status,
                   error_message, model_used, estimated_cost_eur, created_at
            FROM agent_actions
            ORDER BY id DESC
            LIMIT %s
            """,
            (min(limit, 500),),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/metrics/overview")
def overview() -> dict[str, Any]:
    return call_tool("get_daily_metrics", {}, agent_name="dashboard")


DESCRIPTION_BY_TOOL = {
    "discover_businesses": "Create or import discovered businesses for a country and city.",
    "audit_business": "Audit a business web presence and store problems/recommendations.",
    "score_lead": "Score a business opportunity from need, contactability, value, and complexity.",
    "generate_site": "Generate a simple legal website preview for a qualified business.",
    "deploy_site": "Mark a generated site as deployed and expose its preview URL.",
    "prepare_outreach": "Create a transparent outreach email draft with opt-out text.",
    "send_outreach": "Send or dry-run outreach after safety checks and approval.",
    "create_payment_link": "Create a Kiwify payment or care-plan link for an interested business.",
    "get_new_replies": "Placeholder for inbound email reply integration.",
    "get_daily_metrics": "Return overview metrics for dashboard and daily review.",
}
