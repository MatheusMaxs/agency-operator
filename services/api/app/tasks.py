from app.db import init_db
from app.tools import call_tool


def run_tool_job(tool_name: str, payload: dict, agent_name: str = "worker") -> dict:
    init_db()
    return call_tool(tool_name, payload, agent_name=agent_name)
