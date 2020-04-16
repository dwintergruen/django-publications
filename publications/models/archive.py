from django.db import models


class Archive(models.Model):

    name = models.CharField(max_length=2024)
