from django.urls import path

from apps.content.api import PostActionView, PostDetailView, PostListCreateView

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list"),
    path("<uuid:post_id>/", PostDetailView.as_view(), name="post-detail"),
    path("<uuid:post_id>/actions/", PostActionView.as_view(), name="post-actions"),
]
