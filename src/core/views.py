import csv
import requests
import os
from django.views.generic import TemplateView, ListView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from core.models import Dataset
from pathlib import Path


class IndexView(TemplateView):
    template_name = "index.html"


class DatasetView(View):
    def get(self, request):
        today = timezone.now()
        latest_metadata = Dataset.objects.order_by("-download_date").first()

        if latest_metadata and latest_metadata.download_date.date() == today:
            return JsonResponse({"message": "Dataset is already up to date."})

        response = requests.get("https://swapi.dev/api/people/")
        data = response.json().get("results", [])
        filename = (
            f"star_wars_characters_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        print(f"Current working directory: {os.getcwd()}")
        file_path = Path("/opt/src/data") / filename
        print(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data[0].keys())
            for character in data:
                writer.writerow(character.values())
        Dataset.objects.create(filename=filename)

        return JsonResponse({"message": "Dataset downloaded and saved successfully."})


class DatasetListView(ListView):
    model = Dataset
    template_name = "dataset_list.html"  # Jeśli frontend wymaga szablonu
    context_object_name = "datasets"

    def render_to_response(self, context, **response_kwargs):
        # Zwraca dane w formacie JSON
        datasets = list(context["datasets"].values("filename", "download_date"))
        return JsonResponse(datasets, safe=False)
