from app.db import get_conn
from app.settings import settings


class SafetyError(Exception):
    pass


def assert_business_can_be_contacted(business_id: int) -> None:
    with get_conn() as conn:
        business = conn.execute(
            "SELECT id, lead_state FROM businesses WHERE id=%s",
            (business_id,),
        ).fetchone()
        if not business:
            raise SafetyError("Business not found")
        if business["lead_state"] == "DO_NOT_CONTACT":
            raise SafetyError("Business is marked DO_NOT_CONTACT")

        opted_out = conn.execute(
            """
            SELECT 1 FROM business_contacts
            WHERE business_id=%s AND do_not_contact=true
            LIMIT 1
            """,
            (business_id,),
        ).fetchone()
        if opted_out:
            raise SafetyError("A contact for this business opted out")

        duplicate = conn.execute(
            """
            SELECT 1 FROM outreach_messages
            WHERE business_id=%s AND status IN ('SENT','DRY_RUN_SENT')
            LIMIT 1
            """,
            (business_id,),
        ).fetchone()
        if duplicate:
            raise SafetyError("Duplicate outreach blocked")

        sent_today = conn.execute(
            """
            SELECT count(*) AS count FROM outreach_messages
            WHERE status IN ('SENT','DRY_RUN_SENT') AND sent_at::date = CURRENT_DATE
            """,
        ).fetchone()["count"]
        if sent_today >= settings.daily_email_limit:
            raise SafetyError("Daily email limit reached")


def approval_status(target_type: str, target_id: int, approval_type: str) -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT status FROM approvals
            WHERE target_type=%s AND target_id=%s AND approval_type=%s
            """,
            (target_type, target_id, approval_type),
        ).fetchone()
        return row["status"] if row else None


def request_approval(target_type: str, target_id: int, approval_type: str, reason: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO approvals (approval_type, target_type, target_id, reason)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (approval_type, target_type, target_id)
            DO UPDATE SET reason=EXCLUDED.reason
            RETURNING id
            """,
            (approval_type, target_type, target_id, reason),
        ).fetchone()
    return int(row["id"])


def assert_approved_if_required(target_type: str, target_id: int, approval_type: str) -> None:
    if not settings.outreach_requires_approval:
        return
    if approval_status(target_type, target_id, approval_type) != "APPROVED":
        approval_id = request_approval(
            target_type,
            target_id,
            approval_type,
            "Manual approval required before first outreach.",
        )
        raise SafetyError(f"Approval required before sending. approval_id={approval_id}")
