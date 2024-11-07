from datetime import datetime

import petl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from core.models import Dataset
from core.serializers import DatasetSerializer
from core.services import DataProcessor

API_CHARACTERS = "https://swapi.dev/api/people"
API_PLANETS = "https://swapi.dev/api/planets"
processor = DataProcessor(max_pages=50)


class DatasetView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.GET.get("fetch") == "true":
            return self._handle_file_download()

        latest_files = Dataset.objects.order_by("-download_date")
        return render(request, "index.html", {"files": latest_files})

    def _handle_file_download(self) -> HttpResponse:
        time = timezone.localtime()
        raw_data = processor.download_data_from_api(API_CHARACTERS)
        transformed_table = processor.transform_data(data=raw_data, url=API_PLANETS)

        filename, file_path = self._generate_file_path(time)
        petl.tocsv(transformed_table, file_path)

        response = self._create_file_response(file_path, filename)

        dataset_data = {"filename": filename, "download_date": time}
        serializer = DatasetSerializer(data=dataset_data)

        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)

        return response

    def _generate_file_path(self, time: datetime) -> tuple[str, str]:
        filename = f"star_wars_characters_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = f"data/{filename}"
        return filename, file_path

    def _create_file_response(self, file_path: str, filename: str) -> HttpResponse:
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DatasetDetailView(View):
    def get(self, request: HttpRequest, filename: str) -> HttpResponse:
        rows, columns = processor.get_data_from_csv(filename)
        return render(request, "detail_table.html", {"filename": filename, "rows": rows, "columns": columns})


class CountOccurrencesView(View):
    def get(self, request: HttpRequest, filename: str) -> HttpResponse:
        selected_columns = request.GET.getlist("columns")
        num_of_occurrences = self._get_occurrences(filename, selected_columns)
        all_columns = self._get_all_columns(filename)
        return render(
            request,
            "count_data.html",
            {
                "filename": filename,
                "num_of_occurrences": num_of_occurrences,
                "selected_columns": selected_columns,
                "all_columns": all_columns,
            },
        )

    def _get_occurrences(self, filename: str, selected_columns: list[str]) -> list[dict]:
        return processor.count_occurrences(filepath=f"data/{filename}", columns=selected_columns)

    def _get_all_columns(self, filename: str) -> list[str]:
        _, all_columns = processor.get_data_from_csv(filename)
        return all_columns
