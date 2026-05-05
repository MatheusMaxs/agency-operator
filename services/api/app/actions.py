import json
from datetime import datetime, timezone
from typing import Any

from app.db import get_conn


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def log_agent_action(
    *,
    agent_name: str,
    action_type: str,
    status: str,
    target_type: str | None = None,
    target_id: str | None = None,
    input_json: dict[str, Any] | None = None,
    output_json: dict[str, Any] | None = None,
    error_message: str | None = None,
    model_used: str | None = None,
    tokens_input: int = 0,
    tokens_output: int = 0,
    estimated_cost_eur: float = 0,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> int:
    with get_conn() as conn:
        row = conn.execute(
            """
            INSERT INTO agent_actions (
              agent_name, action_type, target_type, target_id, status,
              input_json, output_json, error_message, model_used,
              tokens_input, tokens_output, estimated_cost_eur,
              started_at, finished_at
            ) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            (
                agent_name,
                action_type,
                target_type,
                target_id,
                status,
                json.dumps(input_json or {}),
                json.dumps(output_json or {}),
                error_message,
                model_used,
                tokens_input,
                tokens_output,
                estimated_cost_eur,
                started_at,
                finished_at,
            ),
        ).fetchone()
    return int(row["id"])
