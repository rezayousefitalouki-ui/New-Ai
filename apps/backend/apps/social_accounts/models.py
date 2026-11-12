import hashlib
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class SocialAccount(models.Model):
    class Platform(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        INSTAGRAM = "instagram", "Instagram"

    class Status(models.TextChoices):
        CONNECTED = "connected", "Connected"
        REAUTH_REQUIRED = "reauth_required", "Reauthorization required"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )
    platform = models.CharField(max_length=16, choices=Platform.choices)
    external_id = models.CharField(max_length=128)
    display_name = models.CharField(max_length=160, blank=True)
    username = models.CharField(max_length=160, blank=True)
    access_token_encrypted = models.TextField()
    token_expires_at = models.DateTimeField(null=True, blank=True)
    granted_scopes = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.CONNECTED,
    )
    connected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="social_accounts_connected",
    )
    last_error = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "platform", "external_id"),
                name="uq_social_account_workspace_platform_external",
            )
        ]
        ordering = ("platform", "display_name")

    def set_access_token(self, plaintext):
        from apps.social_accounts.crypto import encrypt_token
        self.access_token_encrypted = encrypt_token(plaintext)

    def get_access_token(self):
        from apps.social_accounts.crypto import decrypt_token
        return decrypt_token(self.access_token_encrypted)

    @property
    def is_expired(self):
        return bool(self.token_expires_at and self.token_expires_at <= timezone.now())

    def __str__(self):
        return f"{self.platform}: {self.display_name or self.external_id}"


class OAuthState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE)
    state_digest = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def digest(cls, state):
        return hashlib.sha256(state.encode("utf-8")).hexdigest()

    @classmethod
    def create_for(cls, user, workspace, state):
        return cls.objects.create(
            user=user,
            workspace=workspace,
            state_digest=cls.digest(state),
            expires_at=timezone.now() + timedelta(minutes=10),
        )

    def consume(self):
        now = timezone.now()
        updated = type(self).objects.filter(
            pk=self.pk,
            consumed_at__isnull=True,
            expires_at__gt=now,
        ).update(consumed_at=now)
        if updated:
            self.consumed_at = now
            return True
        return False
