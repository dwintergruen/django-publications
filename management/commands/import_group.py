from django.core.management.base import BaseCommand, CommandError
from pyzotero import zotero

from publications.models import Type, publication


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def createAuthors(self,authors):

    def import_bibl_items(self,items):
        # publication types
        types = {t.type:t.id for t in Type.objects.all()}

        for i in items:
            typ = i["data"]["itemType"]
            key = i["data"]["key"]
            data = i["data"]
            authors = self.createAuthors(data["creators"])
            archive = self.createArchive(data["archive"])
            month,year = self.getMonth_Year(data["date"])
            tags = self.getTags(data["tags"])
            collections = self.getCollections(data["collections"])

            if typ in types:
                obj,created = publication.get_or_create(key=key)

                attribs = dict(
                    type_id=types[typ],
                    citekey=data['key'],
                    title=data['title'],
                    authors=authors,
                    year=year,
                    date=data["date"],
                    month=month,
                    journal="",
                    book_title="",
                    publisher=data['publisher'],
                    institution="",
                    volume=data['volume'],
                    number=data['numberOfVolume'],
                    pages=data['numPages'],
                    url=data['url'],
                    doi=data['doi'],
                    isbn=data['isbn'],
                    external=False,
                    archive=archive,
                    callNumber=data["callNumber"],
                    rights=data["rights"],
                    extra=data["extra"],
                    collections=collections,
                    tags = tags,
                    dateAdded = data["dateAdded"],
                    dateModified = data["dateModified"]
                )
            for k,v in attribs:
                setattr(obj,k,v)



    def add_arguments(self, parser):
        parser.add_argument('library_id', nargs='+', type=str)
        parser.add_argument('api_key', nargs='+', type=str)

    def handle(self, *args, **options):

        library_id = options["library_id"]
        api_key = options["api_key"]

        zot = zotero.Zotero(library_id,"group",api_key)

        items = zot.items()

        self.import_bibl_items(items)
        self.import_notes(items)
        self.import_attachement(items)




        for poll_id in options['poll_ids']:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
