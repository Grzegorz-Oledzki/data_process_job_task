from datetime import datetime
from pathlib import Path

import petl
import requests
from django.http import Http404


class DataProcessor:
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages

    def download_data_from_api(self, url: str) -> list[dict]:
        response = requests.get(url)
        data = response.json().get("results", [])
        total_items = response.json().get("count")
        page = 2

        while len(data) < total_items and page <= self.max_pages:
            response = requests.get(f"{url}/?page={page}")
            data.extend(response.json().get("results", []))
            page += 1
        return data

    def generate_planet_mapping(self, url: str) -> dict:
        return {record.get("url"): record.get("name") for record in self.download_data_from_api(url)}

    def _format_edited_date(self, edited_date: str) -> str:
        return datetime.strptime(edited_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")

    def transform_data(self, data: list[dict], url: str) -> petl.Table:
        table = petl.fromdicts(data)
        table = petl.addfield(table, "date", lambda rec: self._format_edited_date(rec["edited"]))
        homeworld_mapping = self.generate_planet_mapping(url)
        table = petl.convert(table, "homeworld", lambda v: homeworld_mapping.get(v, v))
        table = petl.cutout(table, "films", "species", "vehicles", "starships", "created", "edited")
        return table

    def get_data_from_csv(self, filename: str) -> tuple[list[dict], list[str]]:
        filepath = Path("data") / filename
        if not filepath.exists():
            raise Http404("File not found.")
        table = petl.fromcsv(str(filepath))
        return list(petl.dicts(table)), table.fieldnames

    def count_occurrences(self, filepath: str, columns: list[str]) -> list[dict]:
        filepath = Path(filepath)
        if not filepath.exists():
            raise Http404("File not found.")
        table = petl.fromcsv(str(filepath))
        counts_table = petl.valuecounts(table, *columns)
        return [{"values": list(row[:-1]), "count": row[-1]} for row in counts_table]
