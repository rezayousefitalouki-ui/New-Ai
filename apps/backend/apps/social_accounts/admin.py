from django.contrib import admin

from apps.social_accounts.models import OAuthState, SocialAccount


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("platform", "display_name", "workspace", "status", "token_expires_at")
    list_filter = ("platform", "status")
    search_fields = ("display_name", "username", "external_id", "workspace__name")
    readonly_fields = ("access_token_encrypted", "created_at", "updated_at")


@admin.register(OAuthState)
class OAuthStateAdmin(admin.ModelAdmin):
    list_display = ("workspace", "user", "created_at", "expires_at", "consumed_at")
    readonly_fields = ("state_digest", "created_at", "expires_at", "consumed_at")
