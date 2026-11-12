from django.urls import path

from apps.social_accounts.api import (
    MetaOAuthCallbackView,
    MetaOAuthStartView,
    SocialAccountDetailView,
    SocialAccountListView,
)

urlpatterns = [
    path("", SocialAccountListView.as_view(), name="social-account-list"),
    path("oauth/meta/start/", MetaOAuthStartView.as_view(), name="meta-oauth-start"),
    path("oauth/meta/callback/", MetaOAuthCallbackView.as_view(), name="meta-oauth-callback"),
    path("<uuid:account_id>/", SocialAccountDetailView.as_view(), name="social-account-detail"),
]
