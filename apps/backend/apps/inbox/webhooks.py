import hashlib
import hmac
import json
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from apps.inbox.models import Conversation, Message
from apps.social_accounts.models import SocialAccount


def _account_for_external_id(external_id):
    return SocialAccount.objects.filter(
        external_id=str(external_id),
        status=SocialAccount.Status.CONNECTED,
    ).first()


def _sent_at(timestamp):
    try:
        value = int(timestamp) / 1000
        return datetime.fromtimestamp(value, tz=dt_timezone.utc)
    except (TypeError, ValueError, OSError):
        return timezone.now()


def _store_message(account, kind, thread_id, participant_id, name, external_id, text, direction, sent_at):
    if not text or not thread_id:
        return
    conversation, _ = Conversation.objects.get_or_create(
        social_account=account,
        kind=kind,
        external_thread_id=str(thread_id),
        defaults={
            "participant_id": str(participant_id or ""),
            "participant_name": (name or "")[:160],
        },
    )
    Message.objects.get_or_create(
        conversation=conversation,
        external_id=str(external_id or ""),
        defaults={
            "sender_id": str(participant_id or ""),
            "sender_name": (name or "")[:160],
            "text": str(text)[:10000],
            "direction": direction,
            "sent_at": sent_at,
        },
    )
    conversation.participant_id = str(participant_id or conversation.participant_id)
    if name:
        conversation.participant_name = str(name)[:160]
    if direction == Message.Direction.INCOMING:
        conversation.unread_count += 1
    conversation.save(update_fields=("participant_id", "participant_name", "unread_count", "updated_at"))


def _ingest(payload):
    for entry in payload.get("entry", []):
        account = _account_for_external_id(entry.get("id"))
        if not account:
            continue
        for event in entry.get("messaging", []):
            message = event.get("message") or {}
            sender = event.get("sender") or {}
            recipient = event.get("recipient") or {}
            sender_id = str(sender.get("id") or "")
            if not message.get("text") or not sender_id:
                continue
            if sender_id == account.external_id:
                continue
            _store_message(
                account=account,
                kind=Conversation.Kind.MESSAGE,
                thread_id=sender_id,
                participant_id=sender_id,
                name=sender.get("name", ""),
                external_id=message.get("mid"),
                text=message["text"],
                direction=Message.Direction.INCOMING,
                sent_at=_sent_at(event.get("timestamp")),
            )
        for change in entry.get("changes", []):
            value = change.get("value") or {}
            item = value.get("item")
            if item not in ("comment", "reply") or not value.get("text"):
                continue
            commenter = value.get("from") or {}
            commenter_id = str(commenter.get("id") or "")
            if commenter_id == account.external_id:
                continue
            comment_id = value.get("comment_id") or value.get("id")
            _store_message(
                account=account,
                kind=Conversation.Kind.COMMENT,
                thread_id=comment_id,
                participant_id=commenter_id,
                name=commenter.get("username") or commenter.get("name", ""),
                external_id=comment_id,
                text=value["text"],
                direction=Message.Direction.INCOMING,
                sent_at=_sent_at(value.get("created_time")),
            )


@method_decorator(csrf_exempt, name="dispatch")
class MetaWebhookView(View):
    def get(self, request):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token", "")
        challenge = request.GET.get("hub.challenge", "")
        configured = settings.META_WEBHOOK_VERIFY_TOKEN
        if mode == "subscribe" and configured and hmac.compare_digest(token, configured):
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponse(status=403)

    def post(self, request):
        secret = settings.META_APP_SECRET
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not secret or not signature.startswith("sha256="):
            return HttpResponse(status=403)
        expected = "sha256=" + hmac.new(
            secret.encode("utf-8"),
            request.body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return HttpResponse(status=403)
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return HttpResponse(status=400)
        _ingest(payload)
        return JsonResponse({"received": True})
