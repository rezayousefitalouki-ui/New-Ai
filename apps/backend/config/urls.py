from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", include("apps.health.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/workspaces/", include("apps.workspaces.urls")),
    path("api/v1/social-accounts/", include("apps.social_accounts.urls")),
    path("api/v1/content/", include("apps.content.urls")),
    path("api/v1/inbox/", include("apps.inbox.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/ai/", include("apps.ai_engine.urls")),
    path("api/v1/video/", include("apps.video_studio.urls")),
]
