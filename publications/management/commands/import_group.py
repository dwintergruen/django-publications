from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from filer.models import Image, Folder
from filer.models import File as Filer_File
from pyzotero import zotero

from publications.models import Type, publication, Publication
from publications.models.archive import Archive
from publications.models.attachment import ImageAttachment, PDFAttachment
from publications.models.collection import Collection
from publications.models.creator import Role,Person, Creator
from publications.models.tag import Tag
import io
import os.path
import  logging
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def import_attachment(self, zot, items,
                          parent_id_as_fn=False,
                          always_upload=False,
                          check_only_filename=False):
        """

        :param zot:
        :param items:
        :param parent_id_as_fn: defaults to false, normally the opriginal filename is used as filename in django storage if true then it uses the id of the parent.
        :param always_upload: defaults to false, upload a file indepent if it already exits, use this if you want the same file with different names in the storage.
        :param check_only_filename: defaults to false, if set don't check hash, just check if name already exists
        speeds the process up because the file is not downloaded from the server.
        :return:
        """
        cnt = 0
        # publication types
        types = {t.zotero_types: t.id for t in Type.objects.all()}

        for i in items:
            typ = i["data"]["itemType"]
            key = i["data"]["key"]
            data = i["data"]
            tags = self.createTags(data["tags"])

            if typ != "attachment":
                continue
            ct = data["contentType"]
            obj_type = None
            if ct.startswith("image/"):
                obj_type = "image"
                New_cls = Image
                folder_name = "images"
            elif "pdf" in ct:
                obj_type = "pdf"
                New_cls = Filer_File
                folder_name = "pdfs"
            else:
                logger.info(f"Don know: {ct}!")
                obj_type = None

            if obj_type:

                filename = data["filename"]
                parentItem = data["parentItem"]

                if parent_id_as_fn:

                    _name,ext = os.path.splitext(filename)
                    filename = parentItem + ext


                if check_only_filename:
                    try:
                        obj_old = New_cls.objects.get(original_filename=filename)  # same object exists already
                        continue
                    except New_cls.DoesNotExist:
                        pass

                bts = zot.file(key)
                f = io.BytesIO(bts)
                file_obj = File(f,name = filename)


                new_obj = New_cls.objects.create(original_filename=filename,
                                                 file=file_obj)

                sha1_neu =  new_obj.sha1
                if not always_upload: #don't save the new object if we have already a files with the same sha
                    try:

                        obj_old = New_cls.objects.get(sha1 = sha1_neu) #same object exists already
                        new_obj.delete()
                        del new_obj
                        new_obj = obj_old
                    except New_cls.DoesNotExist:
                        logger.info("upload new image")

                        fld = Folder.objects.get(name=folder_name)
                        new_obj.folder = fld
                        new_obj.save()

                    except New_cls.MultipleObjectsReturned:
                        logger.warning("Objects exists more than once")
                        images_old = New_cls.objects.filter(sha1=sha1_neu)
                        for i in images_old:
                            logger.warning(i.label)
                        logger.warning(f"I choose the first!")
                        new_obj.delete()
                        del new_obj
                        new_obj = images_old[0]
                else: #always_upload

                    fld = Folder.objects.get(name=folder_name)
                    new_obj.folder = fld
                    new_obj.save()
                try:
                    parent = Publication.objects.get(zoterokey=parentItem)
                    if obj_type == "image":
                        attachment,created = ImageAttachment.objects.get_or_create(zoterokey=key, parent= parent)
                    else:
                        attachment, created = PDFAttachment.objects.get_or_create(zoterokey=key, parent=parent)
                    attachment.file = new_obj
                    for t in tags:
                        attachment.tags.append(t)
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
        return ret


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

                for tag in self.createTags(data.get("tags",[])):
                    obj.tags.add(tag)
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
        parser.add_argument("--key_as_filename",default=False,const=True,nargs="?",help="if set then the filenames of the attachement will be the keys of the parent.")
        parser.add_argument("--always_upload",default=False,const=True,nargs="?",help="always upload the file, normally checks if file with same sha already exists.")
        parser.add_argument("--check_only_filename", default=False, const=True, nargs="?",
                        help="don't check sha1 just the filename for existance of a file.")

    def handle(self, *args, **options):

        logging.basicConfig(level=logging.DEBUG)
        library_id = options["library_id"]
        api_key = options["api_key"]
        key_as_filename = options["key_as_filename"]
        overwrite = options["always_upload"]
        check_only_filename = options["check_only_filename"]

        zot = zotero.Zotero(library_id,"group",api_key)

        items = zot.everything(zot.items())
        imported = self.import_bibl_items(items)
        #self.import_notes(items)
        self.import_attachment(zot, items, parent_id_as_fn=key_as_filename,
                               always_upload=overwrite,
                               check_only_filename=check_only_filename)
        self.import_collectionMetadata(zot)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} items!'))
