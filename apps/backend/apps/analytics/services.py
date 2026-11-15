import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils.dateparse import parse_datetime

from apps.analytics.models import AccountSnapshot, MediaSnapshot


class AnalyticsError(Exception):
    pass


def _get(path, params, token):
    url = f"https://graph.facebook.com/{settings.META_GRAPH_VERSION}/{path.lstrip('/')}?{urlencode({**params, 'access_token': token})}"
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AnalyticsError("دریافت آمار Meta ناموفق بود؛ اتصال و مجوزهای حساب را بررسی کنید.") from exc
    if not isinstance(data, dict) or data.get("error"):
        raise AnalyticsError("Meta این دادهٔ آماری را برای حساب در دسترس قرار نداد.")
    return data


def sync_instagram_account(account):
    if account.platform != account.Platform.INSTAGRAM:
        return None
    if account.status != account.Status.CONNECTED or account.is_expired:
        raise AnalyticsError("اتصال حساب Instagram فعال نیست.")
    token = account.get_access_token()
    profile = _get(account.external_id, {"fields": "username,followers_count,media_count"}, token)
    snapshot = AccountSnapshot.objects.create(
        social_account=account,
        followers_count=profile.get("followers_count"),
        media_count=profile.get("media_count"),
    )
    media = _get(
        f"{account.external_id}/media",
        {"fields": "id,caption,media_type,permalink,timestamp,like_count,comments_count", "limit": 25},
        token,
    )
    for item in media.get("data", []):
        remote_id = item.get("id")
        if not remote_id:
            continue
        MediaSnapshot.objects.update_or_create(
            social_account=account,
            remote_media_id=str(remote_id),
            defaults={
                "caption": str(item.get("caption") or "")[:2200],
                "media_type": str(item.get("media_type") or "")[:32],
                "permalink": str(item.get("permalink") or "")[:500],
                "published_at": parse_datetime(item.get("timestamp", "")) if item.get("timestamp") else None,
                "like_count": item.get("like_count"),
                "comments_count": item.get("comments_count"),
            },
        )
    return snapshot
