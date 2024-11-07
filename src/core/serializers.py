from rest_framework import serializers
from core.models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["filename", "download_date"]
