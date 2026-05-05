import json
from typing import Any

import httpx

from app.settings import settings


def nvidia_configured() -> bool:
    return bool(settings.nvidia_api_key and settings.nvidia_text_model)


def generate_text(system_prompt: str, user_prompt: str, *, temperature: float = 0.3, max_tokens: int = 900) -> str | None:
    if not nvidia_configured():
        return None

    response = httpx.post(
        f"{settings.nvidia_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.nvidia_api_key}", "Content-Type": "application/json"},
        json={
            "model": settings.nvidia_text_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=settings.nvidia_request_timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def generate_design_brief(business: dict[str, Any]) -> dict[str, Any] | None:
    system_prompt = """
You are a senior European local-business web designer.
Return only compact JSON. No markdown.
Create a premium but practical website direction for a small business website preview.
Never invent testimonials, awards, legal claims, or private business facts.
""".strip()
    user_prompt = json.dumps(
        {
            "business": business,
            "offer": {
                "upfront_price_eur": settings.upfront_site_price_eur,
                "care_plan_eur_month": [
                    settings.care_basic_price_eur,
                    settings.care_standard_price_eur,
                    settings.care_growth_price_eur,
                ],
            },
            "required_json_shape": {
                "visual_direction": "short style direction",
                "palette": ["#hex", "#hex", "#hex", "#hex"],
                "hero_headline": "clear headline",
                "hero_subtitle": "clear subtitle",
                "sections": ["hero", "services", "proof", "contact"],
                "cta_primary": "short CTA",
                "services": ["benefit 1", "benefit 2", "benefit 3"],
            },
        },
        ensure_ascii=True,
    )

    try:
        content = generate_text(system_prompt, user_prompt)
        if not content:
            return None
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            content = content.removeprefix("json").strip()
        data = json.loads(content)
        return data if isinstance(data, dict) else None
    except Exception:
        return None
