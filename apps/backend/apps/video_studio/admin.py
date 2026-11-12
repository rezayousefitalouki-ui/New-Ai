from django.contrib import admin
from apps.video_studio.models import RenderJob, VideoProject

@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "workspace", "aspect_ratio", "updated_at")
    search_fields = ("title", "workspace__name")

@admin.register(RenderJob)
class RenderJobAdmin(admin.ModelAdmin):
    list_display = ("project", "status", "started_at", "finished_at")
    list_filter = ("status",)
    readonly_fields = ("output_url", "error_message", "started_at", "finished_at")
