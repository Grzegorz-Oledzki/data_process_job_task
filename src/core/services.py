import requests
import petl
import os
from datetime import datetime
from django.http import Http404


API_PLANETS = "https://swapi.dev/api/planets"


def download_data_from_api(url) -> list[dict]:
    response = requests.get(url)
    compete_data = response.json().get("results", [])
    all_items = response.json().get("count")
    counter = 2

    while len(compete_data) < all_items and counter <= 500:
        response = requests.get(f"{url}/?page={counter}")
        compete_data.extend(response.json().get("results", []))
        counter += 1
    return compete_data


def generate_planet_mapping(url) -> dict:
    data = download_data_from_api(url)
    planets = {}
    for record in data:
        planet_name = record.get("name")
        planet_url = record.get("url")
        planets[planet_url] = planet_name
    return planets


def parse_edited_date(edited_date: str) -> str:
    return datetime.strptime(edited_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")


def transform_data(data: list[dict]):
    table = petl.fromdicts(data)
    table = petl.addfield(table, "date", lambda rec: parse_edited_date(rec["edited"]))
    homeworld_mapping = generate_planet_mapping(API_PLANETS)
    table = petl.convert(table, "homeworld", lambda v: homeworld_mapping.get(v, v))
    table = petl.cutout(
        table, "films", "species", "vehicles", "starships", "created", "edited"
    )
    return table


def get_data_from_csv(filename: str) -> tuple[list[dict[str, any]], list[str]]:
    filepath = os.path.join("data", filename)

    if not os.path.exists(filepath):
        raise Http404("File not found.")

    table = petl.fromcsv(filepath)

    rows = list(petl.dicts(table))
    columns = table.fieldnames
    return rows, columns
