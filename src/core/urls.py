from django.urls import path

from core.views import IndexView, DatasetView, DatasetListView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("download/", DatasetView.as_view(), name="dataset"),
    path("datasets/", DatasetListView.as_view(), name="dataset_list"),
]
