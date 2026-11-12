import uuid

from django.db import models


class AccountSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_account = models.ForeignKey(
        "social_accounts.SocialAccount",
        on_delete=models.CASCADE,
        related_name="analytics_snapshots",
    )
    followers_count = models.PositiveBigIntegerField(null=True, blank=True)
    media_count = models.PositiveBigIntegerField(null=True, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("captured_at",)
        indexes = [
            models.Index(
                fields=("social_account", "captured_at"),
                name="analytics_a_social_9b26a9_idx",
            )
        ]


class MediaSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_account = models.ForeignKey(
        "social_accounts.SocialAccount",
        on_delete=models.CASCADE,
        related_name="media_snapshots",
    )
    remote_media_id = models.CharField(max_length=160)
    caption = models.TextField(blank=True)
    media_type = models.CharField(max_length=32, blank=True)
    permalink = models.URLField(max_length=500, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    like_count = models.PositiveBigIntegerField(null=True, blank=True)
    comments_count = models.PositiveBigIntegerField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("social_account", "remote_media_id"),
                name="uq_analytics_account_remote_media",
            )
        ]
        indexes = [
            models.Index(
                fields=("social_account", "published_at"),
                name="analytics_m_social_8f9c6a_idx",
            )
        ]
