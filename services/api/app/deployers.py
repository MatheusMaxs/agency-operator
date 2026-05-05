import re
from typing import Any

import httpx

from app.settings import settings


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "site"


def deploy_static_site_to_vercel(*, name: str, html: str) -> dict[str, Any] | None:
    if not settings.vercel_token:
        return None

    project_name = slugify(f"{settings.vercel_project_prefix}-{name}")[:52]
    url = "https://api.vercel.com/v13/deployments"
    params: dict[str, str] = {}
    if settings.vercel_team_id:
        params["teamId"] = settings.vercel_team_id

    response = httpx.post(
        url,
        params=params,
        headers={"Authorization": f"Bearer {settings.vercel_token}", "Content-Type": "application/json"},
        json={
            "name": project_name,
            "target": settings.vercel_target,
            "files": [{"file": "index.html", "data": html}],
            "projectSettings": {"framework": None},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    deployment_url = data.get("url")
    if deployment_url and not str(deployment_url).startswith("http"):
        deployment_url = f"https://{deployment_url}"
    return {"provider": "vercel", "project_name": project_name, "url": deployment_url, "raw": data}
