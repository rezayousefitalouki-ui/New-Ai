from django.contrib import admin

from apps.analytics.models import AccountSnapshot, MediaSnapshot


@admin.register(AccountSnapshot)
class AccountSnapshotAdmin(admin.ModelAdmin):
    list_display = ("social_account", "followers_count", "media_count", "captured_at")


@admin.register(MediaSnapshot)
class MediaSnapshotAdmin(admin.ModelAdmin):
    list_display = ("social_account", "remote_media_id", "media_type", "like_count", "comments_count", "published_at")
    search_fields = ("caption", "remote_media_id")
