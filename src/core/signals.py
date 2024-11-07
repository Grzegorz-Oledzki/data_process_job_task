from pathlib import Path

from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.models import Dataset


@receiver(post_delete, sender=Dataset)
def delete_file_after_dataset(sender, instance, **kwargs):
    file_path = Path("data") / instance.filename
    print(f"Attempting to delete file: {file_path}")

    if file_path.exists():
        file_path.unlink()
        print(f"File {file_path} deleted.")
    else:
        print(f"File {file_path} not found.")
