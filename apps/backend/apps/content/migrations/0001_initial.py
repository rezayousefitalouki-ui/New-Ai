import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("social_accounts", "0001_initial"),
        ("workspaces", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("caption", models.TextField(blank=True, max_length=2200)),
                ("media_urls", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("scheduled", "Scheduled"), ("publishing", "Publishing"), ("published", "Published"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="draft", max_length=16)),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_posts", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="posts", to="workspaces.workspace")),
            ],
            options={"ordering": ("-scheduled_at", "-created_at")},
        ),
        migrations.CreateModel(
            name="PostTarget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("publishing", "Publishing"), ("published", "Published"), ("failed", "Failed")], default="queued", max_length=16)),
                ("remote_id", models.CharField(blank=True, max_length=160)),
                ("error_message", models.CharField(blank=True, max_length=300)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="targets", to="content.post")),
                ("social_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="post_targets", to="social_accounts.socialaccount")),
            ],
            options={"ordering": ("social_account__platform", "social_account__display_name")},
        ),
        migrations.AddConstraint(
            model_name="posttarget",
            constraint=models.UniqueConstraint(fields=("post", "social_account"), name="uq_post_social_account"),
        ),
    ]
