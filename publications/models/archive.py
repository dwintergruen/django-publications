from django.db import models

from publications.models.place import Place


class Archive(models.Model):

    name = models.CharField(max_length=2024)
    location = models.ForeignKey(Place,null=True,on_delete=models.SET_NULL)


    def __str__(self):
        return (f"{self.name}_{self.location}")