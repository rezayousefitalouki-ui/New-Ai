import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [("social_accounts", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="AccountSnapshot",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("followers_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("media_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("captured_at", models.DateTimeField(auto_now_add=True)),
                ("social_account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="analytics_snapshots", to="social_accounts.socialaccount")),
            ],
            options={"ordering": ("captured_at",)},
        ),
        migrations.CreateModel(
            name="MediaSnapshot",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("remote_media_id", models.CharField(max_length=160)),
                ("caption", models.TextField(blank=True)),
                ("media_type", models.CharField(blank=True, max_length=32)),
                ("permalink", models.URLField(blank=True, max_length=500)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("like_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("comments_count", models.PositiveBigIntegerField(blank=True, null=True)),
                ("fetched_at", models.DateTimeField(auto_now=True)),
                ("social_account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="media_snapshots", to="social_accounts.socialaccount")),
            ],
            options={"ordering": ("-published_at",)},
        ),
        migrations.AddConstraint(
            model_name="mediasnapshot",
            constraint=models.UniqueConstraint(fields=("social_account", "remote_media_id"), name="uq_analytics_account_remote_media"),
        ),
        migrations.AddIndex(model_name="accountsnapshot", index=models.Index(fields=["social_account", "captured_at"], name="analytics_a_social_9b26a9_idx")),
        migrations.AddIndex(model_name="mediasnapshot", index=models.Index(fields=["social_account", "published_at"], name="analytics_m_social_8f9c6a_idx")),
    ]
