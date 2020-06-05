from django.db import  models
from django.db.models import URLField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

from publications.models import Publication
from publications.models.tag import Tag

class AttachmentType(models.Model):
    name = models.CharField(max_length=2024)
    def __str__(self):
        return self.name


class AbstractAttachment(models.Model):
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    zoterokey = models.CharField(max_length=30, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    type = models.ForeignKey(AttachmentType, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=3000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True

class ImageAttachment(AbstractAttachment):
    file = FilerImageField(null=True,blank=True,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.file)

class PDFAttachment(AbstractAttachment):
    file = FilerFileField(null=True,blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file) + "_" + self.zoterokey


class URLAttachment(AbstractAttachment):
    url = URLField(null=True,blank=True)
    def __str__(self):
        return str(self.url)

class Attachment(AbstractAttachment):
    file = FilerFileField(null=True,blank=True,on_delete=models.CASCADE)
    related_URLAttachment =  models.ManyToManyField(URLAttachment, blank=True)
    def __str__(self):
        return str(self.name)
