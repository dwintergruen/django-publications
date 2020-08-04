from django.contrib.auth.models import User
from django.db import models
from django.db.models import URLField
from django.urls import reverse
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from publications.models import Publication
#from publications.models import Collection
from publications.models.tag import Tag


class AttachmentType(models.Model):
    name = models.CharField(max_length=2024)

    def __str__(self):
        return self.name

class ProcessingType(models.Model):
    name = models.CharField(max_length=2024)

    def __str__(self):
        return self.name


class FormatType(models.Model):
    name = models.CharField(max_length=2024)

    def __str__(self):
        return self.name
class AbstractAttachment(models.Model):
    zoterokey = models.CharField(max_length=30, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    type_of_text = models.ForeignKey(AttachmentType, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=3000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    derived_from = models.ManyToManyField("Attachment", null=True, blank=True)
    lang = models.CharField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

class AbstractPublicationAttachment(AbstractAttachment):
    parent = models.ForeignKey(Publication, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class ImageAttachment(AbstractPublicationAttachment):
    file = FilerImageField(null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)

class PDFAttachment(AbstractPublicationAttachment):
    file = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.file) + "_" + str(self.zoterokey)


class URLAttachment(AbstractPublicationAttachment):
    url = URLField(null=True, blank=True)

    def __str__(self):
        return str(self.url)


class Attachment(AbstractPublicationAttachment):
    file = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)
    related_URLAttachment = models.ManyToManyField(URLAttachment, blank=True)

    def __str__(self):
        return str(self.name)


class CollectionAttachment(AbstractAttachment):
    parent = models.ForeignKey("Collection", on_delete=models.CASCADE)
    file = FilerFileField(null=True, blank=True, on_delete=models.CASCADE)
    type_of_processing = models.ForeignKey(ProcessingType, on_delete=models.SET_NULL, null=True)
    format = models.ForeignKey(FormatType, on_delete=models.SET_NULL, null=True)
    derived_from_collection_attachment = models.ManyToManyField("CollectionAttachment", null=True, blank=True)
    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):

        return reverse("publications:showCollectionAttachment", kwargs={"pk": self.pk})