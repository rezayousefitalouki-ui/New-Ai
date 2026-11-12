from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inbox.meta_messaging import MetaMessagingError, send_reply
from apps.inbox.models import Conversation, Message
from apps.inbox.serializers import ConversationSerializer, MessageSerializer
from apps.workspaces.models import Membership


def _workspace_membership(user, workspace_id):
    try:
        return Membership.objects.select_related("workspace").get(
            user=user,
            workspace_id=workspace_id,
        )
    except (Membership.DoesNotExist, ValueError):
        return None


def _writer(membership):
    return bool(
        membership
        and membership.role in (
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
            Membership.Role.EDITOR,
        )
    )


class ConversationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        membership = _workspace_membership(request.user, workspace_id)
        if not membership:
            return Response(status=status.HTTP_404_NOT_FOUND)
        conversations = Conversation.objects.filter(
            social_account__workspace_id=workspace_id
        ).select_related("social_account").prefetch_related("messages")
        kind = request.query_params.get("kind")
        if kind in (Conversation.Kind.MESSAGE, Conversation.Kind.COMMENT):
            conversations = conversations.filter(kind=kind)
        return Response(
            {"conversations": ConversationSerializer(conversations[:100], many=True).data}
        )


class ConversationDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def _get(self, user, conversation_id):
        return Conversation.objects.select_related(
            "social_account",
            "social_account__workspace",
        ).filter(
            id=conversation_id,
            social_account__workspace__memberships__user=user,
        ).first()

    def get(self, request, conversation_id):
        conversation = self._get(request.user, conversation_id)
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        messages = conversation.messages.all()
        conversation.unread_count = 0
        conversation.save(update_fields=("unread_count",))
        return Response(
            {
                "conversation": ConversationSerializer(conversation).data,
                "messages": MessageSerializer(messages, many=True).data,
            }
        )


class ConversationReplyView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, conversation_id):
        conversation = Conversation.objects.select_related(
            "social_account",
            "social_account__workspace",
        ).filter(
            id=conversation_id,
            social_account__workspace__memberships__user=request.user,
        ).first()
        if not conversation:
            return Response(status=status.HTTP_404_NOT_FOUND)
        membership = _workspace_membership(
            request.user,
            conversation.social_account.workspace_id,
        )
        if not _writer(membership):
            return Response(status=status.HTTP_403_FORBIDDEN)
        text = str(request.data.get("text", "")).strip()
        if not text or len(text) > 2000:
            return Response(
                {"text": ["متن پاسخ الزامی است و باید کمتر از ۲۰۰۰ نویسه باشد."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            remote_id = send_reply(conversation, text)
        except (MetaMessagingError, ValueError) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        with transaction.atomic():
            message = Message.objects.create(
                conversation=conversation,
                external_id=remote_id,
                sender_id=conversation.social_account.external_id,
                sender_name=conversation.social_account.display_name,
                text=text,
                direction=Message.Direction.OUTGOING,
                sent_at=timezone.now(),
            )
            conversation.save(update_fields=("updated_at",))
        return Response(
            {"message": MessageSerializer(message).data},
            status=status.HTTP_201_CREATED,
        )
