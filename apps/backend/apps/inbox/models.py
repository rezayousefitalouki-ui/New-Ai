import uuid

from django.db import models


class Conversation(models.Model):
    class Kind(models.TextChoices):
        MESSAGE = "message", "Message"
        COMMENT = "comment", "Comment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_account = models.ForeignKey(
        "social_accounts.SocialAccount",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    external_thread_id = models.CharField(max_length=160)
    participant_id = models.CharField(max_length=160, blank=True)
    participant_name = models.CharField(max_length=160, blank=True)
    unread_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("social_account", "kind", "external_thread_id"),
                name="uq_inbox_conversation_external_thread",
            )
        ]
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.social_account} · {self.kind} · {self.participant_name}"


class Message(models.Model):
    class Direction(models.TextChoices):
        INCOMING = "incoming", "Incoming"
        OUTGOING = "outgoing", "Outgoing"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    external_id = models.CharField(max_length=160, blank=True)
    sender_id = models.CharField(max_length=160, blank=True)
    sender_name = models.CharField(max_length=160, blank=True)
    text = models.TextField(max_length=10000)
    direction = models.CharField(max_length=12, choices=Direction.choices)
    sent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("conversation", "external_id"),
                condition=~models.Q(external_id=""),
                name="uq_inbox_message_external_id",
            )
        ]
        ordering = ("sent_at", "created_at")

    def __str__(self):
        return f"{self.direction}: {self.text[:60]}"
