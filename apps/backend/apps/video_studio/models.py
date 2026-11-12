import uuid
from django.conf import settings
from django.db import models

class VideoProject(models.Model):
    class AspectRatio(models.TextChoices):
        PORTRAIT = "9:16", "Portrait"
        SQUARE = "1:1", "Square"
        LANDSCAPE = "16:9", "Landscape"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="video_projects")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="video_projects")
    title = models.CharField(max_length=160)
    aspect_ratio = models.CharField(max_length=8, choices=AspectRatio.choices, default=AspectRatio.PORTRAIT)
    storyboard = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-updated_at",)

class RenderJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RENDERING = "rendering", "Rendering"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(VideoProject, on_delete=models.CASCADE, related_name="renders")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    output_url = models.CharField(max_length=500, blank=True)
    error_message = models.CharField(max_length=300, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ("-created_at",)
