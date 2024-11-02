from django.urls import path
from .views import DatasetView, DatasetDetailView

urlpatterns = [
    path("", DatasetView.as_view(), name="index"),  # Upewnij się, że nazwa to 'index'
    path("dataset/", DatasetView.as_view(), name="dataset"),
    path("dataset/<str:filename>/", DatasetDetailView.as_view(), name="dataset_detail"),
]
