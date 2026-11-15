from rest_framework import serializers
from apps.video_studio.models import RenderJob, VideoProject

class VideoProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProject
        fields = ("id", "title", "aspect_ratio", "storyboard", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
    def validate_storyboard(self, value):
        scenes = value.get("scenes") if isinstance(value, dict) else None
        if not isinstance(scenes, list) or not 1 <= len(scenes) <= 12:
            raise serializers.ValidationError("استوری‌بورد باید بین ۱ تا ۱۲ صحنه داشته باشد.")
        total = 0
        cleaned = []
        for scene in scenes:
            if not isinstance(scene, dict):
                raise serializers.ValidationError("ساختار هر صحنه معتبر نیست.")
            title = str(scene.get("title") or "").strip()[:160]
            text = str(scene.get("text") or "").strip()[:600]
            visual = str(scene.get("visual") or "").strip()[:600]
            try:
                duration = max(1, min(15, int(scene.get("duration_seconds", 4))))
            except (TypeError, ValueError):
                raise serializers.ValidationError("مدت صحنه باید بین ۱ تا ۱۵ ثانیه باشد.") from None
            if not title and not text and not visual:
                raise serializers.ValidationError("هر صحنه باید متن یا توصیف داشته باشد.")
            total += duration
            cleaned.append({"title": title, "text": text, "visual": visual, "duration_seconds": duration})
        if total > 120:
            raise serializers.ValidationError("مدت کل ویدیو نمی‌تواند بیشتر از ۱۲۰ ثانیه باشد.")
        return {"title": str(value.get("title") or "")[:160], "scenes": cleaned}

class RenderJobSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    class Meta:
        model = RenderJob
        fields = ("id", "project", "project_title", "status", "output_url", "error_message", "started_at", "finished_at", "created_at")
        read_only_fields = fields
