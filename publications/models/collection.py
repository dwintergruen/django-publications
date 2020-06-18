import json
from collections import defaultdict, Counter

import dateparser as dateparser
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from publications.models import Publication
from publications.models.attachment import PDFAttachment, AttachmentType

from publications.models.publication import ATTACHMENTTYPES
import logging
logger = logging.getLogger(__name__)

class Collection(models.Model):

    zoterokey = models.CharField(max_length=100)
    name = models.CharField(default="",max_length=2024)
    items = models.ManyToManyField(Publication)
    parent = models.ForeignKey("Collection", blank=True, null=True,on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    counts = models.CharField(default={},max_length=10000,blank=True,null=True)

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

    def _count_attachments_old(self):
        counts = defaultdict(int)
        for i in self.items.all():
            if i.has_pdf:
                counts["pdf"] += 1
            for type in ATTACHMENTTYPES:
                if getattr(i, "has_%s" % type):
                    counts[type] += 1

        self.counts = json.dumps(counts)

    def _count_attachments(self,attachmenttypes=ATTACHMENTTYPES):
        counts = defaultdict(int)
        for i in self.items.all():
            if i.has_pdf:
                counts["pdf"] += 1
            for type in attachmenttypes:
                try:
                    tp = AttachmentType.objects.get(name=type)
                except AttachmentType.DoesNotExist:
                    continue
                attms = i.attachment_set.filter(type_of_text=tp).count()
                if attms > 0:
                    counts[type] += 1

        self.counts = json.dumps(counts)

    def save(self, *args, **kwargs):
        """count all attachments by type"""

        if kwargs.get("count",False):
            if self.id: #objects is saved
                self._count_attachments()

        if "count" in kwargs:
            del kwargs["count"]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("publications:collectionView",kwargs={"pk":self.pk})

    def getCounts(self):
        cnts = json.loads(self.counts)
        return cnts

    def timeDistribution(self,only_year = False):

        time_list = []
        for item in self.items.all():
            date = item.date
            year = item.year
            if not date:
                date = "%s-1-1"%year
            try:
                month = dateparser.parse(date).month
                year  = dateparser.parse(date).year
            except TypeError:
                if year:
                    year =year
                    month = 1
                    logger.debug(f"no date for {item} -- {date} - take year {year}")
                else:
                    logger.error(f"no date for {item} -- {date}")
                    continue
            except AttributeError:
                if year:
                    year = year
                    month = 1
                    logger.debug(f"no date for {item} -- {date} - take year {year}")
                else:
                    logger.error(f"no date for {item} -- {date}")
                    continue


            if not only_year:
                time_list.append((month,year))
            else:
                time_list.append(year)

        counted_mount_year = Counter(time_list)
        return counted_mount_year




