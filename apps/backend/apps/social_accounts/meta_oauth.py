import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings


class MetaOAuthError(Exception):
    pass


def _request_json(url, timeout=15):
    try:
        with urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MetaOAuthError("ارتباط با Meta انجام نشد؛ دوباره تلاش کنید.") from exc
    if isinstance(payload, dict) and payload.get("error"):
        raise MetaOAuthError("Meta درخواست اتصال را نپذیرفت.")
    return payload


def authorization_url(state):
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_OAUTH_CALLBACK_URI,
        "response_type": "code",
        "scope": ",".join(settings.META_OAUTH_SCOPES),
        "state": state,
    }
    return f"https://www.facebook.com/{settings.META_GRAPH_VERSION}/dialog/oauth?{urlencode(params)}"


def fetch_managed_assets(code):
    graph = f"https://graph.facebook.com/{settings.META_GRAPH_VERSION}"
    token_payload = _request_json(
        f"{graph}/oauth/access_token?{urlencode({
            'client_id': settings.META_APP_ID,
            'client_secret': settings.META_APP_SECRET,
            'redirect_uri': settings.META_OAUTH_CALLBACK_URI,
            'code': code,
        })}"
    )
    user_token = token_payload.get("access_token")
    if not user_token:
        raise MetaOAuthError("دریافت توکن از Meta ناموفق بود.")

    long_lived_payload = _request_json(
        f"{graph}/oauth/access_token?{urlencode({
            'grant_type': 'fb_exchange_token',
            'client_id': settings.META_APP_ID,
            'client_secret': settings.META_APP_SECRET,
            'fb_exchange_token': user_token,
        })}"
    )
    user_token = long_lived_payload.get("access_token", user_token)
    expires_in = int(long_lived_payload.get("expires_in", token_payload.get("expires_in", 0)) or 0)
    pages_payload = _request_json(
        f"{graph}/me/accounts?{urlencode({
            'fields': 'id,name,access_token,instagram_business_account{id,username}',
            'access_token': user_token,
        })}"
    )
    assets = []
    for page in pages_payload.get("data", []):
        page_token = page.get("access_token")
        page_id = page.get("id")
        if not page_token or not page_id:
            continue
        assets.append({
            "platform": "facebook",
            "external_id": str(page_id),
            "display_name": page.get("name", ""),
            "username": "",
            "access_token": page_token,
            "expires_in": expires_in,
        })
        instagram = page.get("instagram_business_account") or {}
        if instagram.get("id"):
            assets.append({
                "platform": "instagram",
                "external_id": str(instagram["id"]),
                "display_name": instagram.get("username") or page.get("name", ""),
                "username": instagram.get("username", ""),
                "access_token": page_token,
                "expires_in": expires_in,
            })
    return assets
