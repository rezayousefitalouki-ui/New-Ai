from django.urls import path

from apps.ai_engine.api import BrandProfileView, GenerationDetailView, GenerationListCreateView

urlpatterns = [
    path("brand/", BrandProfileView.as_view(), name="brand-profile"),
    path("generations/", GenerationListCreateView.as_view(), name="generations"),
    path("generations/<uuid:generation_id>/", GenerationDetailView.as_view(), name="generation-detail"),
]
