from django.urls import path

from apps.analytics.api import AnalyticsView

urlpatterns = [path("", AnalyticsView.as_view(), name="analytics")]
