import pysolr as pysolr
import tqdm as tqdm
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from filer.models import Image, Folder
from filer.models import File as Filer_File
from pyzotero import zotero
import pyzotero.zotero_errors
from publications.models import Type, publication, Publication
from publications.models.archive import Archive
from publications.models.attachment import ImageAttachment, PDFAttachment
from publications.models.collection import Collection
from publications.models.creator import Role,Person, Creator
from publications.models.ner_object import NER_type, NER_object
from publications.models.place import Place
from publications.models.tag import Tag
import io
import os.path
import  logging
logger = logging.getLogger(__name__)
FIELDS= ["id","date","year","journal","title","people_ss","organization_ss","location_ss"]


def add_or_change_publication(r, collection):

    solr_id = r["id"]

    tp = Type.objects.get(type="Journal")
    publication,created = Publication.objects.get_or_create(solr_id = solr_id, type = tp)
    try:
        publication.year = int(r["year"])
    except TypeError:
        logger.error(f"{r['id']} year not an integer: {r['year']}")

    publication.journal = r.get("journal",None)

    for person in r.get("people_ss",[]):
        type, created = NER_type.objects.get_or_create(name="person")
        ner_object, created = NER_object.objects.get_or_create(type=type, name = person)
        publication.ner_objects.add(ner_object)

    for location in r.get("location_ss", []):
        type, created = NER_type.objects.get_or_create(name="location")
        ner_object, created = NER_object.objects.get_or_create(type=type, name=location)
        publication.ner_objects.add(ner_object)

    for location in r.get("organisation_ss", []):
        type, created = NER_type.objects.get_or_create(name="location")
        ner_object, created = NER_object.objects.get_or_create(type=type, name=location)
        publication.ner_objects.add(ner_object)


    publication.save()
    collection.items.add(publication)
    collection.save(no_count=True)

class Command(BaseCommand):

    def import_from_solr(self,solr_url,qs,collection):

        collection, created = Collection.objects.get_or_create(name=collection)

        solr = pysolr.Solr(solr_url)
        res = solr.search(qs,rows=1,fl="id")
        logger.debug(f"searched: {qs} and found {res.hits} hits.")

        LENGTH = 1000
        for start in tqdm.tqdm(range(0,res.hits,LENGTH)):
            res = solr.search(qs,start=start,rows=LENGTH,fl=FIELDS)
            for r in res:
                add_or_change_publication(r,collection)

    def add_arguments(self, parser):
        parser.add_argument('--solr_url', type=str)
        parser.add_argument('--qs', type=str)
        parser.add_argument('--collection', type = str)


    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG)
        self.import_from_solr(options["solr_url"],options["qs"],options["collection"])








