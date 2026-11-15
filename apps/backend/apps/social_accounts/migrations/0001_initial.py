import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0002_alter_user_options_alter_user_groups"),
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OAuthState",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("state_digest", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="workspaces.workspace")),
            ],
        ),
        migrations.CreateModel(
            name="SocialAccount",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("platform", models.CharField(choices=[("facebook", "Facebook"), ("instagram", "Instagram")], max_length=16)),
                ("external_id", models.CharField(max_length=128)),
                ("display_name", models.CharField(blank=True, max_length=160)),
                ("username", models.CharField(blank=True, max_length=160)),
                ("access_token_encrypted", models.TextField()),
                ("token_expires_at", models.DateTimeField(blank=True, null=True)),
                ("granted_scopes", models.JSONField(blank=True, default=list)),
                ("status", models.CharField(choices=[("connected", "Connected"), ("reauth_required", "Reauthorization required"), ("error", "Error")], default="connected", max_length=24)),
                ("last_error", models.CharField(blank=True, max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("connected_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="social_accounts_connected", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="social_accounts", to="workspaces.workspace")),
            ],
            options={"ordering": ("platform", "display_name")},
        ),
        migrations.AddConstraint(
            model_name="socialaccount",
            constraint=models.UniqueConstraint(fields=("workspace", "platform", "external_id"), name="uq_social_account_workspace_platform_external"),
        ),
    ]
