from datetime import datetime

import pytest

from core.models import Dataset
from core.services import DataProcessor

processor = DataProcessor(max_pages=50)

pytestmark = pytest.mark.django_db


@pytest.fixture
def filename():
    return "test.csv"


@pytest.mark.parametrize(
    "filename, download_date", [("test.csv", datetime.now().strftime("%Y-%m-%d")), ("example.csv", datetime.now().strftime("%Y-%m-%d"))]
)
def test_create_dataset(filename: str, download_date: str):
    dataset = Dataset.objects.create(filename=filename, download_date=download_date)
    assert dataset.filename == filename
    assert dataset.download_date.strftime("%Y-%m-%d") == download_date


@pytest.mark.parametrize("filename, download_date", [("test.csv", "2024-11-01"), ("example.csv", "2024-11-02")])
def test_dataset_str(filename: str, download_date: str):
    dataset = Dataset.objects.create(filename=filename, download_date=download_date)
    assert str(dataset) == f"{filename}"


@pytest.mark.parametrize("column, column_value, num_of_count", [(["mass"], "unknown", 23), (["hair_color"], "brown", 16)])
def test_count_single_column(filename: str, column: list, column_value: str, num_of_count: int):
    num_of_occurrences = processor.count_occurrences(filepath=f"src/data/{filename}", columns=column)
    num_of_occurrences_dict = {item["values"][0]: item["values"][1] for item in num_of_occurrences[1:]}
    assert column[0] in num_of_occurrences[0].get("values")
    assert num_of_occurrences_dict.get(column_value) == num_of_count


@pytest.mark.parametrize(
    "columns, column_value, num_of_count", [(["hair_color", "skin_color"], "brown, fair", 7), (["eye_color", "gender"], "brown, male", 15)]
)
def test_count_multiple_columns(filename: str, columns: list, column_value: str, num_of_count: int):
    num_of_occurrences = processor.count_occurrences(filepath=f"src/data/{filename}", columns=columns)
    num_of_occurrences_dict = {", ".join(map(str, item["values"][:-1])): item["values"][-1] for item in num_of_occurrences[1:]}

    assert all(item in num_of_occurrences[0].get("values") for item in columns)
    assert num_of_occurrences_dict.get(column_value) == num_of_count
