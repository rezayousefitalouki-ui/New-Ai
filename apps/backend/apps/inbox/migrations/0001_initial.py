import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("social_accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Conversation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("kind", models.CharField(choices=[("message", "Message"), ("comment", "Comment")], max_length=16)),
                ("external_thread_id", models.CharField(max_length=160)),
                ("participant_id", models.CharField(blank=True, max_length=160)),
                ("participant_name", models.CharField(blank=True, max_length=160)),
                ("unread_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("social_account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="conversations", to="social_accounts.socialaccount")),
            ],
            options={"ordering": ("-updated_at",)},
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("external_id", models.CharField(blank=True, max_length=160)),
                ("sender_id", models.CharField(blank=True, max_length=160)),
                ("sender_name", models.CharField(blank=True, max_length=160)),
                ("text", models.TextField(max_length=10000)),
                ("direction", models.CharField(choices=[("incoming", "Incoming"), ("outgoing", "Outgoing")], max_length=12)),
                ("sent_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="inbox.conversation")),
            ],
            options={"ordering": ("sent_at", "created_at")},
        ),
        migrations.AddConstraint(
            model_name="conversation",
            constraint=models.UniqueConstraint(fields=("social_account", "kind", "external_thread_id"), name="uq_inbox_conversation_external_thread"),
        ),
        migrations.AddConstraint(
            model_name="message",
            constraint=models.UniqueConstraint(condition=models.Q(("external_id", ""), _negated=True), fields=("conversation", "external_id"), name="uq_inbox_message_external_id"),
        ),
    ]
