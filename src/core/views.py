import os

import petl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from core.models import Dataset
from core.services import (
    count_occurrences,
    download_data_from_api,
    get_data_from_csv,
    transform_data,
)

API_PEOPLE = "https://swapi.dev/api/people/"


class DatasetView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        time = timezone.localtime()

        if request.GET.get("fetch") == "true":
            raw_data = download_data_from_api(API_PEOPLE)
            transformed_table = transform_data(raw_data)

            data_dir = "data"
            filename = f"star_wars_characters_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = f"{data_dir}/{filename}"

            petl.tocsv(transformed_table, file_path)

            with open(file_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="text/csv")
                response["Content-Disposition"] = f'attachment; filename="{filename}"'

            Dataset.objects.create(filename=filename, download_date=time)

            return response

        latest_files = Dataset.objects.order_by("-download_date")
        return render(request, "index.html", {"files": latest_files})


class DatasetDetailView(View):
    def get(self, request: HttpRequest, filename: str) -> HttpResponse:
        rows, columns = get_data_from_csv(filename)
        context = {
            "filename": filename,
            "rows": rows,
            "columns": columns,
        }
        return render(request, "detail_table.html", context)


class CountOccurrencesView(View):
    def get(self, request: HttpRequest, filename: str) -> HttpResponse:
        _, all_columns = get_data_from_csv(filename)
        selected_columns: list[str] = request.GET.getlist("columns")
        filepath = os.path.join("data", filename)
        counts = count_occurrences(filepath, selected_columns)
        return render(
            request,
            "count_data.html",
            {
                "filename": filename,
                "count_data": counts,
                "selected_columns": selected_columns,
                "all_columns": all_columns,
            },
        )
