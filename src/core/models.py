from django.db import models


class Dataset(models.Model):
    filename = models.CharField(max_length=255)
    download_date = models.DateTimeField(auto_now_add=True)
