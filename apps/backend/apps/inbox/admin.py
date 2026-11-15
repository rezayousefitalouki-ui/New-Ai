from django.contrib import admin

from apps.inbox.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("external_id", "sender_id", "sender_name", "text", "direction", "sent_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("participant_name", "kind", "social_account", "unread_count", "updated_at")
    list_filter = ("kind", "social_account__platform")
    search_fields = ("participant_name", "participant_id", "external_thread_id")
    inlines = (MessageInline,)
