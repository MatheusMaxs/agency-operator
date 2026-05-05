import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


API_INTERNAL_URL = os.getenv("API_INTERNAL_URL", "http://api:8000")

app = FastAPI(title="Agency Operator MCP Bridge", version="0.1.0")


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}
    agent_name: str = "hermes"


@app.get("/health")
async def health() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{API_INTERNAL_URL}/health")
    return {"ok": True, "api": response.json()}


@app.get("/manifest")
async def manifest() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{API_INTERNAL_URL}/tools")
    response.raise_for_status()
    tools = response.json()["tools"]
    return {
        "name": "agency-operator-tools",
        "description": "Logged business tools for the agency operator system.",
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": {"type": "object", "additionalProperties": True},
            }
            for tool in tools
        ],
    }


@app.post("/call")
async def call_tool(call: ToolCall) -> dict[str, Any]:
    payload = dict(call.arguments)
    payload.setdefault("agent_name", call.agent_name)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{API_INTERNAL_URL}/tools/{call.tool}", json=payload)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return {"tool": call.tool, "result": response.json()}


@app.post("/jsonrpc")
async def jsonrpc(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": await manifest()}

    if method == "tools/call":
        tool = params.get("name") or params.get("tool")
        arguments = params.get("arguments") or {}
        if not tool:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing tool name"}}
        try:
            result = await call_tool(ToolCall(tool=tool, arguments=arguments, agent_name=params.get("agent_name", "hermes")))
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except HTTPException as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": exc.status_code, "message": str(exc.detail)}}

    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
