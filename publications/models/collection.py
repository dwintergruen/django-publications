from django.db import models

from publications.models import Publication


class Collection(models.Model):

    zoterokey = models.CharField(max_length=100)
    name = models.CharField(default="",max_length=2024)
    items = models.ManyToManyField(Publication)
    parent = models.ForeignKey("Collection", blank=True, null=True,on_delete=models.SET_NULL)


    def __str__(self):
        return self.name