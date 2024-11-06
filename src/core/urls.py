from django.urls import path

from core.views import CountOccurrencesView, DatasetDetailView, DatasetView

urlpatterns = [
    path("", DatasetView.as_view(), name="index"),
    path("dataset/", DatasetView.as_view(), name="dataset"),
    path("dataset/<str:filename>/", DatasetDetailView.as_view(), name="dataset_detail"),
    path(
        "detail_data/<str:filename>/count_occurrences/",
        CountOccurrencesView.as_view(),
        name="count_occurrences",
    ),
]
