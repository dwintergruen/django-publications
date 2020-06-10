from django.db import models

class NER_type(models.Model):
    class Meta:
        app_label = 'publications'

    name = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class NER_object(models.Model):
    class Meta:
        app_label = 'publications'

    type = models.ForeignKey(NER_type, on_delete=models.CASCADE)
    name = models.CharField(max_length=5000)

    def __str__(self):
        return self.name
