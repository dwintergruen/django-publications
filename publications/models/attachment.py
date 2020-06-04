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
    type = models.ForeignKey(AttachmentType, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.file) + "_" + self.zoterokey


class URLAttachment(models.Model):
    zoterokey = models.CharField(max_length=30,blank=True,null=True)
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    url = URLField(null=True,blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    type = models.ForeignKey(AttachmentType, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.url)


class Attachment(models.Model):
    #zoterokey = models.CharField(max_length=30,blank=True,null=True)
    parent = models.ForeignKey(Publication,on_delete=models.CASCADE)
    file = FilerFileField(null=True,blank=True,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    name =  models.CharField(max_length=3000,blank=True,null=True)
    related_URLAttachment =  models.ManyToManyField(URLAttachment, blank=True)
    type = models.ForeignKey(AttachmentType, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return str(self.name)
