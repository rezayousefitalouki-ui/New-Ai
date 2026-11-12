import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class PublishingError(Exception):
    pass


def _post(path, params):
    url = f"https://graph.facebook.com/{settings.META_GRAPH_VERSION}/{path.lstrip('/')}"
    request = Request(
        url,
        data=urlencode(params).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise PublishingError("Meta انتشار محتوا را نپذیرفت؛ اتصال یا مجوز را بررسی کنید.") from exc
    if not isinstance(payload, dict) or payload.get("error"):
        raise PublishingError("Meta انتشار محتوا را نپذیرفت؛ مجوز یا رسانه معتبر نیست.")
    return payload


def publish_target(target):
    account = target.social_account
    if account.status != account.Status.CONNECTED or account.is_expired:
        raise PublishingError("توکن این حساب منقضی یا غیرفعال است؛ حساب را دوباره متصل کنید.")
    token = account.get_access_token()
    media_urls = target.post.media_urls
    caption = target.post.caption
    if account.platform == account.Platform.FACEBOOK:
        if media_urls:
            result = _post(
                f"{account.external_id}/photos",
                {"url": media_urls[0], "caption": caption, "access_token": token},
            )
        else:
            result = _post(
                f"{account.external_id}/feed",
                {"message": caption, "access_token": token},
            )
        return str(result.get("post_id") or result.get("id") or "")

    if account.platform == account.Platform.INSTAGRAM:
        if len(media_urls) != 1:
            raise PublishingError("انتشار Instagram در این نسخه فقط یک تصویر عمومی HTTPS می‌پذیرد.")
        if not media_urls[0].lower().split("?")[0].endswith((".jpg", ".jpeg")):
            raise PublishingError("برای Instagram در این نسخه فقط تصویر JPEG پشتیبانی می‌شود.")
        container = _post(
            f"{account.external_id}/media",
            {
                "image_url": media_urls[0],
                "caption": caption,
                "access_token": token,
            },
        )
        creation_id = container.get("id")
        if not creation_id:
            raise PublishingError("Meta ظرف رسانه را ایجاد نکرد.")
        published = _post(
            f"{account.external_id}/media_publish",
            {"creation_id": creation_id, "access_token": token},
        )
        return str(published.get("id") or "")

    raise PublishingError("این شبکه هنوز به انتشار متصل نشده است.")
