from django.urls import path
from apps.video_studio.api import ProjectDetailView, ProjectListCreateView, RenderCreateView, RenderFileView, RenderJobListView

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="video-projects"),
    path("projects/<uuid:project_id>/", ProjectDetailView.as_view(), name="video-project"),
    path("projects/<uuid:project_id>/render/", RenderCreateView.as_view(), name="video-render-create"),
    path("renders/", RenderJobListView.as_view(), name="video-renders"),
    path("renders/<uuid:render_id>/file/", RenderFileView.as_view(), name="video-render-file"),
]
