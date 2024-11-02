from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.views import View
from core.models import Dataset
from core.services import download_data_from_api, transform_data, get_data_from_csv
import petl

API_PEOPLE = "https://swapi.dev/api/people/"


class DatasetView(View):
    def get(self, request):
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
    def get(self, request, filename):
        rows, columns = get_data_from_csv(filename)

        return render(
            request,
            "dataset_detail.html",
            {
                "rows": rows,
                "columns": columns,
                "filename": filename,
                "offset": 10,
            },
        )
