from django.contrib import admin
from .models import Dataset


class DatasetAdmin(admin.ModelAdmin):

    list_display = ("filename", "download_date", "id")
    search_fields = ("filename",)
    list_filter = ("download_date",)
    ordering = ("-download_date",)
    list_per_page = 20


admin.site.register(Dataset, DatasetAdmin)
