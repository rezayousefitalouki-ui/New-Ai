from rest_framework import serializers

from apps.inbox.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "sender_name", "text", "direction", "sent_at")
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source="social_account.platform", read_only=True)
    account_name = serializers.CharField(source="social_account.display_name", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "kind",
            "participant_id",
            "participant_name",
            "platform",
            "account_name",
            "unread_count",
            "updated_at",
            "last_message",
        )
        read_only_fields = fields

    def get_last_message(self, conversation):
        message = conversation.messages.order_by("-sent_at").first()
        return MessageSerializer(message).data if message else None
