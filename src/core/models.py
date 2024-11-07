from pathlib import Path

from django.db import models


class Dataset(models.Model):
    filename = models.CharField(max_length=255)
    download_date = models.DateTimeField()

    def delete(self, *args, **kwargs):

        file_path = Path("data") / self.filename
        print(f"Attempting to delete: {file_path}")

        if file_path.exists():
            file_path.unlink()

        super().delete(*args, **kwargs)
