import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class MetaMessagingError(Exception):
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
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MetaMessagingError("پاسخ شبکهٔ اجتماعی ارسال نشد؛ مجوز و اتصال را بررسی کنید.") from exc
    if not isinstance(result, dict) or result.get("error"):
        raise MetaMessagingError("پاسخ شبکهٔ اجتماعی ارسال نشد؛ مجوز یا شناسه معتبر نیست.")
    return result


def send_reply(conversation, text):
    account = conversation.social_account
    if account.status != account.Status.CONNECTED or account.is_expired:
        raise MetaMessagingError("توکن این حساب منقضی است؛ حساب را دوباره متصل کنید.")
    token = account.get_access_token()
    if conversation.kind == conversation.Kind.COMMENT:
        edge = "replies" if account.platform == account.Platform.INSTAGRAM else "comments"
        result = _post(
            f"{conversation.external_thread_id}/{edge}",
            {"message": text, "access_token": token},
        )
    else:
        if not conversation.participant_id:
            raise MetaMessagingError("شناسهٔ گیرنده در رویداد دریافتی موجود نیست.")
        result = _post(
            f"{account.external_id}/messages",
            {
                "recipient": json.dumps({"id": conversation.participant_id}),
                "message": json.dumps({"text": text}),
                "messaging_type": "RESPONSE",
                "access_token": token,
            },
        )
    return str(result.get("message_id") or result.get("id") or "")
