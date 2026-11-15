from django.urls import path

from apps.workspaces.api import (
    WorkspaceDetailView,
    WorkspaceListCreateView,
    WorkspaceMemberDetailView,
    WorkspaceMembersView,
)

urlpatterns = [
    path("", WorkspaceListCreateView.as_view(), name="workspace-list"),
    path("<uuid:workspace_id>/", WorkspaceDetailView.as_view(), name="workspace-detail"),
    path("<uuid:workspace_id>/members/", WorkspaceMembersView.as_view(), name="workspace-members"),
    path(
        "<uuid:workspace_id>/members/<uuid:membership_id>/",
        WorkspaceMemberDetailView.as_view(),
        name="workspace-member-detail",
    ),
]
