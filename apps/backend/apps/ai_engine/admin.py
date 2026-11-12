from django.contrib import admin

from apps.ai_engine.models import AIGeneration, BrandProfile


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "industry", "workspace", "updated_at")
    search_fields = ("business_name", "industry")


@admin.register(AIGeneration)
class AIGenerationAdmin(admin.ModelAdmin):
    list_display = ("kind", "status", "workspace", "provider_model", "usage_tokens", "created_at")
    list_filter = ("kind", "status")
    readonly_fields = ("result", "provider_model", "usage_tokens", "error_message")
