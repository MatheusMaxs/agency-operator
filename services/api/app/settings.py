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


settings = Settings()
