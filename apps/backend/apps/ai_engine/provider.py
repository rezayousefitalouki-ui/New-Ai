import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class ProviderError(Exception):
    pass


def generate(kind, brief, brand):
    api_key = settings.AI_PROVIDER_API_KEY
    model = settings.AI_PROVIDER_MODEL
    base_url = settings.AI_PROVIDER_BASE_URL.rstrip("/")
    if not api_key or not model:
        raise ProviderError("ارائه‌دهندهٔ هوش مصنوعی پیکربندی نشده است.")
    schemas = {
        "ideas": "Return {items:[{title,format,objective,hook,cta}]} with 5 distinct ideas.",
        "script": "Return {hook,scenes:[{title,narration,visual,duration_seconds}],caption,cta,hashtags}.",
        "caption": "Return {caption,short_version,cta,hashtags}.",
        "strategy": "Return {pillars:[{name,objective,topics}],weekly_cadence,experiments,success_metrics}.",
    }
    system = (
        "You are a Persian-first Instagram content assistant. Return valid JSON only. "
        "Use the supplied brand context. Do not invent facts, guarantees, or performance metrics. "
        "Respect forbidden terms and write in Persian unless the brief requests another language. "
        + schemas[kind]
    )
    context = {
        "brand": {
            "business_name": brand.business_name,
            "industry": brand.industry,
            "products": brand.products,
            "audience": brand.audience,
            "voice": brand.voice,
            "preferred_topics": brand.preferred_topics,
            "forbidden_terms": brand.forbidden_terms,
        },
        "brief": brief,
    }
    body = json.dumps({
        "model": model,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
        ],
    }).encode("utf-8")
    request = Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=90) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderError("درخواست به ارائه‌دهندهٔ هوش مصنوعی ناموفق بود.") from exc
    try:
        result = json.loads(payload["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise ProviderError("پاسخ ساختاریافتهٔ ارائه‌دهنده معتبر نیست.") from exc
    if not isinstance(result, dict):
        raise ProviderError("خروجی هوش مصنوعی باید یک شیء JSON باشد.")
    usage = payload.get("usage") or {}
    return result, model, usage.get("total_tokens")
