from django.contrib import admin

from apps.content.models import Post, PostTarget


class PostTargetInline(admin.TabularInline):
    model = PostTarget
    extra = 0
    readonly_fields = ("status", "remote_id", "error_message", "attempts", "published_at")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "workspace", "status", "scheduled_at", "created_at")
    list_filter = ("status",)
    search_fields = ("caption", "workspace__name")
    inlines = (PostTargetInline,)
