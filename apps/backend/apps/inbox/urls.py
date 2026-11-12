from django.urls import path

from apps.inbox.api import ConversationDetailView, ConversationListView, ConversationReplyView
from apps.inbox.webhooks import MetaWebhookView

urlpatterns = [
    path("", ConversationListView.as_view(), name="inbox-list"),
    path("<uuid:conversation_id>/", ConversationDetailView.as_view(), name="inbox-detail"),
    path("<uuid:conversation_id>/reply/", ConversationReplyView.as_view(), name="inbox-reply"),
    path("webhook/meta/", MetaWebhookView.as_view(), name="meta-webhook"),
]
