import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BrandProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("business_name", models.CharField(blank=True, max_length=160)),
                ("industry", models.CharField(blank=True, max_length=160)),
                ("products", models.TextField(blank=True, max_length=4000)),
                ("audience", models.TextField(blank=True, max_length=2000)),
                ("voice", models.CharField(default="friendly", max_length=40)),
                ("preferred_topics", models.JSONField(blank=True, default=list)),
                ("forbidden_terms", models.JSONField(blank=True, default=list)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("workspace", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="brand_profile", to="workspaces.workspace")),
            ],
        ),
        migrations.CreateModel(
            name="AIGeneration",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("kind", models.CharField(choices=[("ideas", "Content ideas"), ("script", "Script"), ("caption", "Caption"), ("strategy", "Strategy")], max_length=16)),
                ("brief", models.TextField(max_length=5000)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("running", "Running"), ("succeeded", "Succeeded"), ("failed", "Failed")], default="queued", max_length=16)),
                ("result", models.JSONField(blank=True, null=True)),
                ("provider_model", models.CharField(blank=True, max_length=120)),
                ("usage_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("error_message", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ai_generations", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_generations", to="workspaces.workspace")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
