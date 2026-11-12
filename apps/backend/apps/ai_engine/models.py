import uuid

from django.conf import settings
from django.db import models


class BrandProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="brand_profile",
    )
    business_name = models.CharField(max_length=160, blank=True)
    industry = models.CharField(max_length=160, blank=True)
    products = models.TextField(blank=True, max_length=4000)
    audience = models.TextField(blank=True, max_length=2000)
    voice = models.CharField(max_length=40, default="friendly")
    preferred_topics = models.JSONField(default=list, blank=True)
    forbidden_terms = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name or str(self.workspace_id)


class AIGeneration(models.Model):
    class Kind(models.TextChoices):
        IDEAS = "ideas", "Content ideas"
        SCRIPT = "script", "Script"
        CAPTION = "caption", "Caption"
        STRATEGY = "strategy", "Strategy"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="ai_generations")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ai_generations")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    brief = models.TextField(max_length=5000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    result = models.JSONField(null=True, blank=True)
    provider_model = models.CharField(max_length=120, blank=True)
    usage_tokens = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
