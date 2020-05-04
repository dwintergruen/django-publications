from django.db import models

from publications.models import Publication
from publications.models.attachment import PDFAttachment

class Collection(models.Model):

    zoterokey = models.CharField(max_length=100)
    name = models.CharField(default="",max_length=2024)
    items = models.ManyToManyField(Publication)
    parent = models.ForeignKey("Collection", blank=True, null=True,on_delete=models.SET_NULL)


    def get_pdfs(self):
        rets = {}
        for item in self.items.all():
            paths = []
            pdfs = PDFAttachment.objects.filter(parent=item)
            for pdf in pdfs:
                fl = pdf.file.file.path
                paths.append(fl)

            rets[item] = paths
        return rets

    def __str__(self):
        return self.name