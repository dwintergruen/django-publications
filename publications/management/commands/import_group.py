from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from filer.models import Image, Folder
from pyzotero import zotero

from publications.models import Type, publication, Publication
from publications.models.archive import Archive
from publications.models.attachment import ImageAttachment
from publications.models.collection import Collection
from publications.models.creator import Role,Person, Creator
from publications.models.tag import Tag
import io
import  logging
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def import_attachment(self,zot,items):
        cnt = 0
        # publication types
        types = {t.zotero_types: t.id for t in Type.objects.all()}

        for i in items:
            typ = i["data"]["itemType"]
            key = i["data"]["key"]
            data = i["data"]

            type_known = False
            if typ != "attachment":
                continue
            ct = data["contentType"]
            if ct.startswith("image/"): #is an image
                filename = data["filename"]
                parentItem = data["parentItem"]


                bts = zot.file(key)
                f = io.BytesIO(bts)
                #file_obj._committed = False
                #file_obj = open("/tmp/Francesco di Giorgio_Trattato di architettura e macchine_Ashburnham 361_f 25r_FACSIMILI del Museo Galileo.jpg","rb")
                file_obj = File(f,name = filename)

                image = Image.objects.create(original_filename=filename,
                                             file=file_obj)

                sha1_neu =  image.sha1
                try:
                    image_old = Image.objects.get(sha1 = sha1_neu)
                    del image
                    image = image_old
                except Image.DoesNotExist:
                    print("upload new")
                    fld = Folder.objects.get(name="images")
                    image.folder = fld
                    image.save()
                except Image.MultipleObjectsReturned:
                    logger.warning("Image objects exists more than once")
                    images_old = Image.objects.filter(sha1=sha1_neu)
                    for i in images_old:
                        logger.warning(i.label)
                    logger.warning(f"I choose the first!")
                    del image
                    image = images_old[0]

                try:
                    parent = Publication.objects.get(zoterokey=parentItem)
                    attachment,created = ImageAttachment.objects.get_or_create(zoterokey=key, parent= parent)
                    attachment.file = image
                    #attachment.parent = Publication.objects.get_or_create(zoterokey=parentItem)
                    attachment.save()
                except Publication.DoesNotExist:
                    print(f"Parent Item {parentItem} has to exist attachement not created!")
            else:
                print(f"not importing: {ct}")

    def createAuthors(self,creators):
        """ deals with
        [{'creatorType': 'author',
        'firstName': 'Francesco',
        'lastName': 'di Giorgio'}],
        """
        ret = []
        for creator in creators:
            role, created = Role.objects.get_or_create(typ = creator["creatorType"])
            if "firstName" in creator and "lastName" in creator:
                person, created = Person.objects.get_or_create(firstName= creator["firstName"],lastName=creator["lastName"])
            elif "name" in creator:
                person, created = Person.objects.get_or_create(name=creator["name"])
            else:
                raise ValueError("Neither firstName and lastName nor Name in creator dataset!")


            creator = Creator(role = role, person = person)
            creator.save()
            ret.append(creator)
        return ret

    def createArchive(self,archive):
        if archive.strip() == "":
            return None
        archive,created = Archive.objects.get_or_create(name = archive)
        return archive

    def createTags(self,tags):
        ret = []
        for tag in tags:
            tag,created = Tag.objects.get_or_create(name = tag["tag"])
            ret.append(tag)
        return tags


    def import_bibl_items(self,items):
        cnt = 0
        # publication types
        types = {t.zotero_types:t.id for t in Type.objects.all()}

        for i in items:
            typ = i["data"]["itemType"]
            key = i["data"]["key"]
            data = i["data"]

            type_known = False
            for t in types:
                if typ in t.split(","):
                    type_known = True
                    break

            if type_known:
                authors = self.createAuthors(data["creators"])
                archive = self.createArchive(data.get("archive",""))
                # month,year = self.getMonth_Year(data["date"])
                tags = self.createTags(data["tags"])

                attribs = dict(
                    type_id=types[typ],
                    #citekey=data['key'],
                    title=data['title'],
                    authors=authors,
                    #year=year,
                    date=data["date"],
                    #month=month,
                    journal="",
                    book_title="",
                    publisher=data.get('publisher',""),
                    artworkMedium = data.get("artworkMedium",""),
                    artworkSize = data.get("artworkSize",""),
                    institution="",
                    volume=data.get('volume',0),
                    number=data.get('numberOfVolume',0),
                    pages=data.get('numPages',""),
                    url=data['url'],
                    doi=data.get('doi',""),
                    isbn=data.get('isbn',""),
                    external=False,
                    archive=archive,
                    callNumber=data.get(    "callNumber",""),
                    rights=data["rights"],
                    extra=data["extra"],
                    tags = tags,
                    dateAdded = data["dateAdded"],
                    dateModified = data["dateModified"]
                )


                try:
                    obj = publication.Publication.objects.get(zoterokey=key)
                except publication.Publication.DoesNotExist:
                    obj = publication.Publication(zoterokey=key)

                for k,v in attribs.items():
                    setattr(obj,k,v)

                obj.save()
                for c in data["collections"]:
                    collection,created = Collection.objects.get_or_create(zoterokey = c)
                    collection.items.add(obj)
                    collection.save()
                cnt +=1
            else:
                self.stdout.write(f"{typ} not in types, not imported!")
        return cnt


    def import_collectionMetadata(self,zot):
        collections = zot.collections()
        for collection in collections:
            data = collection["data"]
            zoterokey = data["key"]
            name = data["name"]
            parent = data["parentCollection"]

            col,created = Collection.objects.get_or_create(zoterokey=zoterokey)
            col.name = name
            if parent:
                parent,created = Collection.objects.get_or_create(zoterokey=zoterokey)
                col.parent = parent
            col.save()


    def add_arguments(self, parser):
        parser.add_argument('library_id',  type=str)
        parser.add_argument('api_key', type=str)

    def handle(self, *args, **options):

        library_id = options["library_id"]
        api_key = options["api_key"]

        zot = zotero.Zotero(library_id,"group",api_key)

        items = zot.items()
        imported = self.import_bibl_items(items)
        #self.import_notes(items)
        self.import_attachment(zot,items)
        self.import_collectionMetadata(zot)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} items!'))
