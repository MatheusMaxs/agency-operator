import json
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.db import get_conn
from app.settings import settings


def package_catalog() -> dict[str, dict[str, Any]]:
    return {
        "LOCAL_BUSINESS_SITE": {
            "label": "Complete local business website",
            "amount": settings.upfront_site_price_eur * 100,
            "currency": settings.offer_currency,
            "recurring": False,
            "checkout_url": settings.kiwify_site_checkout_url or settings.kiwify_checkout_url,
        },
        "CARE_BASIC": {
            "label": "Care Basic",
            "amount": settings.care_basic_price_eur * 100,
            "currency": settings.offer_currency,
            "recurring": True,
            "checkout_url": settings.kiwify_care_basic_checkout_url or settings.kiwify_checkout_url,
        },
        "CARE_STANDARD": {
            "label": "Care Standard",
            "amount": settings.care_standard_price_eur * 100,
            "currency": settings.offer_currency,
            "recurring": True,
            "checkout_url": settings.kiwify_care_standard_checkout_url or settings.kiwify_checkout_url,
        },
        "CARE_GROWTH": {
            "label": "Care Growth",
            "amount": settings.care_growth_price_eur * 100,
            "currency": settings.offer_currency,
            "recurring": True,
            "checkout_url": settings.kiwify_care_growth_checkout_url or settings.kiwify_checkout_url,
        },
    }


def append_query_params(url: str, params: dict[str, Any]) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: str(value) for key, value in params.items() if value is not None and value != ""})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def create_kiwify_payment_link(business_id: int, package_name: str = "LOCAL_BUSINESS_SITE") -> dict[str, Any]:
    package_key = _normalize_package_name(package_name)
    package = package_catalog().get(package_key)
    if not package:
        raise ValueError(f"Unknown package: {package_name}")
    if not package["checkout_url"]:
        raise ValueError("Kiwify checkout URL is not configured")

    with get_conn() as conn:
        business = conn.execute("SELECT id, name, email, lead_state FROM businesses WHERE id=%s", (business_id,)).fetchone()
        if not business:
            raise ValueError("Business not found")

        checkout_url = append_query_params(
            package["checkout_url"],
            {
                "business_id": business_id,
                "package": package_key,
                "amount_eur": int(package["amount"]) // 100,
                "utm_source": "agency_operator",
                "utm_medium": "payment_link",
                "utm_campaign": package_key.lower(),
                "utm_content": f"business_{business_id}",
            },
        )

        if package["recurring"]:
            row = conn.execute(
                """
                INSERT INTO subscriptions (business_id, provider, plan_name, status, amount, currency, checkout_url)
                VALUES (%s,'kiwify',%s,'PENDING',%s,%s,%s)
                RETURNING id, business_id, provider, plan_name, status, amount, currency, checkout_url
                """,
                (business_id, package_key, package["amount"], package["currency"], checkout_url),
            ).fetchone()
        else:
            row = conn.execute(
                """
                INSERT INTO payments (business_id, package_name, provider, payment_status, amount, currency, checkout_url)
                VALUES (%s,%s,'kiwify','PENDING',%s,%s,%s)
                RETURNING id, business_id, package_name, provider, payment_status, amount, currency, checkout_url
                """,
                (business_id, package_key, package["amount"], package["currency"], checkout_url),
            ).fetchone()
            conn.execute(
                """
                UPDATE businesses SET lead_state='PAYMENT_LINK_SENT', updated_at=now()
                WHERE id=%s AND lead_state <> 'PAID'
                """,
                (business_id,),
            )

    result = dict(row)
    result["recurring"] = bool(package["recurring"])
    result["label"] = package["label"]
    result["amount_eur"] = int(package["amount"]) / 100
    return result


def handle_kiwify_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    business_id = _find_int(payload, {"business_id", "businessId", "external_reference", "externalReference", "utm_content", "utmContent", "reference"})
    customer_email = _find_str(payload, {"email", "customer_email", "customerEmail", "buyer_email", "buyerEmail", "client_email", "clientEmail"})
    package_name = _normalize_package_name(
        _find_str(payload, {"package", "package_name", "packageName", "product_name", "productName", "product", "plan_name", "planName"})
    )
    status = _normalize_status(_find_str(payload, {"status", "payment_status", "paymentStatus", "order_status", "orderStatus", "subscription_status", "subscriptionStatus", "event"}))
    provider_payment_id = _find_str(payload, {"payment_id", "paymentId", "transaction_id", "transactionId", "order_id", "orderId", "sale_id", "saleId", "id"})
    provider_checkout_id = _find_str(payload, {"checkout_id", "checkoutId", "checkout_session_id", "checkoutSessionId", "checkout"})
    provider_subscription_id = _find_str(payload, {"subscription_id", "subscriptionId", "subscription"})
    invoice_url = _find_str(payload, {"invoice_url", "invoiceUrl", "receipt_url", "receiptUrl", "boleto_url", "payment_url", "paymentUrl"})
    amount = _amount_from_payload(payload, package_name)
    currency = (_find_str(payload, {"currency", "currency_code"}) or settings.offer_currency).lower()
    raw_payload = json.dumps(payload)

    with get_conn() as conn:
        if business_id is None and customer_email:
            business = conn.execute(
                "SELECT id FROM businesses WHERE lower(email)=lower(%s) ORDER BY id DESC LIMIT 1",
                (customer_email,),
            ).fetchone()
            business_id = int(business["id"]) if business else None
        if business_id is None:
            raise ValueError("Could not match Kiwify webhook to a business")

        is_subscription = bool(provider_subscription_id) or "CARE_" in package_name or "SUBSCRIPTION" in package_name
        if is_subscription:
            row = _upsert_subscription(
                conn,
                business_id=business_id,
                provider_subscription_id=provider_subscription_id,
                plan_name=package_name,
                status="ACTIVE" if status == "PAID" else status,
                amount=amount,
                currency=currency,
                raw_payload=raw_payload,
            )
        else:
            row = _upsert_payment(
                conn,
                business_id=business_id,
                package_name=package_name,
                status=status,
                amount=amount,
                currency=currency,
                provider_payment_id=provider_payment_id,
                provider_checkout_id=provider_checkout_id,
                invoice_url=invoice_url,
                raw_payload=raw_payload,
            )
            if status == "PAID":
                conn.execute("UPDATE businesses SET lead_state='PAID', updated_at=now() WHERE id=%s", (business_id,))

    return {"ok": True, "business_id": business_id, "status": status, "record": dict(row)}


def _upsert_payment(
    conn: Any,
    *,
    business_id: int,
    package_name: str,
    status: str,
    amount: int,
    currency: str,
    provider_payment_id: str | None,
    provider_checkout_id: str | None,
    invoice_url: str | None,
    raw_payload: str,
) -> Any:
    existing = None
    if provider_payment_id:
        existing = conn.execute(
            "SELECT id FROM payments WHERE provider='kiwify' AND provider_payment_id=%s ORDER BY id DESC LIMIT 1",
            (provider_payment_id,),
        ).fetchone()
    if not existing:
        existing = conn.execute(
            """
            SELECT id FROM payments
            WHERE provider='kiwify' AND business_id=%s AND package_name=%s
            ORDER BY id DESC LIMIT 1
            """,
            (business_id, package_name),
        ).fetchone()

    if existing:
        return conn.execute(
            """
            UPDATE payments
            SET payment_status=%s, amount=%s, currency=%s, provider_payment_id=%s,
                provider_checkout_id=%s, invoice_url=%s, raw_payload=%s::jsonb,
                paid_at=CASE WHEN %s='PAID' THEN now() ELSE paid_at END
            WHERE id=%s
            RETURNING *
            """,
            (status, amount, currency, provider_payment_id, provider_checkout_id, invoice_url, raw_payload, status, existing["id"]),
        ).fetchone()

    return conn.execute(
        """
        INSERT INTO payments (
          business_id, package_name, provider, provider_payment_id, provider_checkout_id,
          payment_status, amount, currency, invoice_url, raw_payload, paid_at
        ) VALUES (%s,%s,'kiwify',%s,%s,%s,%s,%s,%s,%s::jsonb,CASE WHEN %s='PAID' THEN now() ELSE NULL END)
        RETURNING *
        """,
        (business_id, package_name, provider_payment_id, provider_checkout_id, status, amount, currency, invoice_url, raw_payload, status),
    ).fetchone()


def _upsert_subscription(
    conn: Any,
    *,
    business_id: int,
    provider_subscription_id: str | None,
    plan_name: str,
    status: str,
    amount: int,
    currency: str,
    raw_payload: str,
) -> Any:
    existing = None
    if provider_subscription_id:
        existing = conn.execute(
            "SELECT id FROM subscriptions WHERE provider='kiwify' AND provider_subscription_id=%s ORDER BY id DESC LIMIT 1",
            (provider_subscription_id,),
        ).fetchone()
    if not existing:
        existing = conn.execute(
            """
            SELECT id FROM subscriptions
            WHERE provider='kiwify' AND business_id=%s AND plan_name=%s
            ORDER BY id DESC LIMIT 1
            """,
            (business_id, plan_name),
        ).fetchone()

    if existing:
        return conn.execute(
            """
            UPDATE subscriptions
            SET provider_subscription_id=%s, status=%s, amount=%s, currency=%s,
                raw_payload=%s::jsonb, started_at=CASE WHEN %s='ACTIVE' THEN coalesce(started_at, now()) ELSE started_at END,
                updated_at=now()
            WHERE id=%s
            RETURNING *
            """,
            (provider_subscription_id, status, amount, currency, raw_payload, status, existing["id"]),
        ).fetchone()

    return conn.execute(
        """
        INSERT INTO subscriptions (
          business_id, provider, provider_subscription_id, plan_name, status,
          amount, currency, raw_payload, started_at
        ) VALUES (%s,'kiwify',%s,%s,%s,%s,%s,%s::jsonb,CASE WHEN %s='ACTIVE' THEN now() ELSE NULL END)
        RETURNING *
        """,
        (business_id, provider_subscription_id, plan_name, status, amount, currency, raw_payload, status),
    ).fetchone()


def _normalize_status(value: str | None) -> str:
    text = (value or "").lower()
    if any(token in text for token in ["paid", "approved", "completed", "active"]):
        return "PAID"
    if any(token in text for token in ["refused", "rejected", "failed", "chargeback"]):
        return "FAILED"
    if any(token in text for token in ["cancel", "expired", "refund"]):
        return "CANCELED"
    return "PENDING"


def _normalize_package_name(value: str | None) -> str:
    text = (value or "LOCAL_BUSINESS_SITE").strip().upper().replace("-", "_").replace(" ", "_")
    if "CARE" in text and "BASIC" in text:
        return "CARE_BASIC"
    if "CARE" in text and "STANDARD" in text:
        return "CARE_STANDARD"
    if "CARE" in text and "GROWTH" in text:
        return "CARE_GROWTH"
    if "LOCAL" in text or "WEBSITE" in text or "SITE" in text:
        return "LOCAL_BUSINESS_SITE"
    return text


def _amount_from_payload(payload: dict[str, Any], package_name: str) -> int:
    package = package_catalog().get(package_name)
    if package:
        return int(package["amount"])
    raw = _find_number(payload, {"amount", "price", "total", "total_amount", "totalAmount", "value"})
    if raw is None:
        return settings.upfront_site_price_eur * 100
    return int(raw if raw > 10000 else raw * 100)


def _find_str(value: Any, keys: set[str]) -> str | None:
    found = _find_value(value, keys)
    if found is None:
        return None
    return str(found)


def _find_int(value: Any, keys: set[str]) -> int | None:
    found = _find_value(value, keys)
    if found is None:
        return None
    match = re.search(r"\d+", str(found))
    return int(match.group(0)) if match else None


def _find_number(value: Any, keys: set[str]) -> float | None:
    found = _find_value(value, keys)
    if found is None:
        return None
    try:
        return float(str(found).replace(",", "."))
    except ValueError:
        return None


def _find_value(value: Any, keys: set[str]) -> Any:
    normalized_keys = {key.lower() for key in keys}
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in normalized_keys:
                return item
        for item in value.values():
            found = _find_value(item, keys)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = _find_value(item, keys)
            if found is not None:
                return found
    return None
