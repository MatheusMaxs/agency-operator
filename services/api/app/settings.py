from dataclasses import dataclass
import os


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    return int(value)


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agency:change_this_password@postgres:5432/agency_operator",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    brand_name: str = os.getenv("BRAND_NAME", "Agency Operator")
    base_public_url: str = os.getenv("BASE_PUBLIC_URL", "http://127.0.0.1:8000")
    dashboard_public_url: str = os.getenv("DASHBOARD_PUBLIC_URL", "http://127.0.0.1:3000")
    outreach_requires_approval: bool = env_bool("OUTREACH_REQUIRES_APPROVAL", True)
    email_dry_run: bool = env_bool("EMAIL_DRY_RUN", True)
    daily_email_limit: int = env_int("DAILY_EMAIL_LIMIT", 25)
    from_email: str = os.getenv("FROM_EMAIL", "hello@example.com")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    offer_currency: str = os.getenv("OFFER_CURRENCY", "eur")
    upfront_site_price_eur: int = env_int("UPFRONT_SITE_PRICE_EUR", 1000)
    care_basic_price_eur: int = env_int("CARE_BASIC_PRICE_EUR", 49)
    care_standard_price_eur: int = env_int("CARE_STANDARD_PRICE_EUR", 99)
    care_growth_price_eur: int = env_int("CARE_GROWTH_PRICE_EUR", 149)
    nvidia_api_key: str = os.getenv("NVIDIA_API_KEY", "")
    nvidia_base_url: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    nvidia_text_model: str = os.getenv("NVIDIA_TEXT_MODEL", "")
    nvidia_vision_model: str = os.getenv("NVIDIA_VISION_MODEL", "")
    nvidia_request_timeout: int = env_int("NVIDIA_REQUEST_TIMEOUT", 60)
    kiwify_checkout_url: str = os.getenv("KIWIFY_CHECKOUT_URL", "")
    kiwify_site_checkout_url: str = os.getenv("KIWIFY_SITE_CHECKOUT_URL", "")
    kiwify_care_basic_checkout_url: str = os.getenv("KIWIFY_CARE_BASIC_CHECKOUT_URL", "")
    kiwify_care_standard_checkout_url: str = os.getenv("KIWIFY_CARE_STANDARD_CHECKOUT_URL", "")
    kiwify_care_growth_checkout_url: str = os.getenv("KIWIFY_CARE_GROWTH_CHECKOUT_URL", "")
    kiwify_webhook_token: str = os.getenv("KIWIFY_WEBHOOK_TOKEN", "")
    vercel_token: str = os.getenv("VERCEL_TOKEN", "")
    vercel_team_id: str = os.getenv("VERCEL_TEAM_ID", "")
    vercel_project_prefix: str = os.getenv("VERCEL_PROJECT_PREFIX", "agency-preview")
    vercel_target: str = os.getenv("VERCEL_TARGET", "preview")


settings = Settings()
