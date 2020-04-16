from django.db import  models
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

from publications.models import Publication


class ImageAttachment(models.Model):
    zoterokey = models.CharField(max_length=30)
    parent = models.ForeignKey(Publication,on_delete=models.CASCADE)
    file = FilerImageField(null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)

class PDFAttachment(models.Model):

    zoterokey = models.CharField(max_length=30)
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    file = FilerFileField(null=True,blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)

