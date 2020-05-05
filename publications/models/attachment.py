from django.db import  models
from django.db.models import URLField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

from publications.models import Publication
from publications.models.tag import Tag


class ImageAttachment(models.Model):
    zoterokey = models.CharField(max_length=30,blank=True,null=True)
    parent = models.ForeignKey(Publication,on_delete=models.CASCADE)
    file = FilerImageField(null=True,blank=True,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    def __str__(self):
        return str(self.file)

class PDFAttachment(models.Model):

    zoterokey = models.CharField(max_length=30,blank=True,null=True)
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    file = FilerFileField(null=True,blank=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return str(self.file)


class URLAttachment(models.Model):
    zoterokey = models.CharField(max_length=30,blank=True,null=True)
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    url = URLField(null=True,blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return str(self.file)


