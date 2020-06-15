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
from publications.models.place import Place
from publications.models.tag import Tag
import io
import os.path
import  logging
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def import_attachment(self, zot, items,
                          parent_id_as_fn=False,
                          attachment_id_as_fn=False,
                          always_upload=False,
                          check_only_filename=False,
                          no_upload = False,
                          in_folder = None):
        """
        :param zot:
        :param items:
        :param parent_id_as_fn: defaults to false, normally the opriginal filename is used as filename in django storage if true then it uses the id of the parent.
        :param attachment_id_as_fn: defaults to false, normally the opriginal filename is used as filename in django storage if true then it uses the id of the parent.
        :param always_upload: defaults to false, upload a file indepent if it already exits, use this if you want the same file with different names in the storage.
        :param check_only_filename: defaults to false, if set don't check hash, just check if name already exists
        speeds the process up because the file is not downloaded from the server.
        :param in_folder: patho to folder to check if file already downloaded
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

                filename = data.get("filename",None)

                if not filename:
                    logger.error(f"{key} has no filename. not imported!")
                    continue

                parentItem = data.get("parentItem",None)

                if not parentItem:
                    logger.error(f"{key} has no parent item. not imported!")
                    continue


                if parent_id_as_fn:

                    _name,ext = os.path.splitext(filename)
                    filename = parentItem + ext

                if attachment_id_as_fn:

                    _name,ext = os.path.splitext(filename)
                    filename = key + ext



                new_obj = None
                if check_only_filename:
                    try:
                        new_obj = New_cls.objects.get(original_filename=filename)  # same object exists already
                        logger.info(f"{filename} already exist!")

                    except New_cls.DoesNotExist:
                        try:
                            New_cls.objects.get(original_filename=filename.lower())
                            logger.info(f"{filename.lower()} already exist!")
                            continue
                        except:
                            pass
                    except New_cls.MultipleObjectsReturned:
                        logger.error(f"{filename} exist more than once!")
                        logger.error(f"I choose the first!")
                        new_obj=New_cls.objects.filter(original_filename=filename)[0]

                try:
                    parent = Publication.objects.get(zoterokey=parentItem)
                except Publication.DoesNotExist:
                    print(f"Parent Item {parentItem} has to exist attachment not created!")
                    continue

                if no_upload:
                    attachment, created = PDFAttachment.objects.get_or_create(zoterokey=key, parent=parent, name=filename)
                    attachment.save()

                else:
                    if not new_obj: #haven'T found a file already above
                        logger.debug(f"Might have to created a new object. ")
                        path = None
                        if in_folder:
                            path = os.path.join(in_folder, key) + ".pdf"
                            if not os.path.exists(path):
                                path = os.path.join(in_folder, key.lower()) + ".pdf"
                                if not os.path.exists(path):
                                    path = None


                        if path:
                            logging.debug("read file from infolder")
                            f = open(path,"rb")
                        else:
                            try:
                                logging.debug("read file from zotero")
                                bts = zot.file(key)
                            except pyzotero.zotero_errors.ResourceNotFound:
                                logger.error(f"Ressource not found: {key} ")
                                continue
                            f = io.BytesIO(bts)

                        file_obj = File(f,name = filename)


                        new_obj = New_cls.objects.create(original_filename=filename,
                                                         file=file_obj)

                        sha1_neu =  new_obj.sha1
                        logger.debug(f"created a new object {new_obj}")
                        if not always_upload: #don't save the new object if we have already a files with the same sha
                            logger.debug(f"not always upload selected")
                            logger.debug(f"check if it already exists, with the same sha1_neu")

                            objs_old = New_cls.objects.filter(sha1 = sha1_neu).exclude(id=new_obj.id) #same object exists already
                            if len(objs_old) == 1:
                                new_obj.delete()
                                del new_obj
                                logger.debug(f"already exists, will use this one. delete the new object again.")
                                new_obj = objs_old[0]

                            elif  len(objs_old) == 0:
                                logger.info("upload new object")

                                fld = Folder.objects.get(name=folder_name)
                                new_obj.folder = fld
                                new_obj.save()

                            else:
                                logger.warning("Objects exists more than once")

                                for i in objs_old:
                                    logger.warning(i.label)
                                logger.warning(f"I choose the first!")
                                new_obj.delete()
                                del new_obj
                                new_obj = objs_old[0]
                                fld = Folder.objects.get(name=folder_name)
                                new_obj.folder = fld
                        else: #always_upload
                            logger.debug(f"always upload selected")
                            fld,created = Folder.objects.get_or_create(name=folder_name)
                            new_obj.folder = fld
                            new_obj.save()

                    logger.debug(f"will create attachment now")
                    if obj_type == "image":
                        attachment,created = ImageAttachment.objects.get_or_create(zoterokey=key, parent= parent)
                    else:

                        attachment, created = PDFAttachment.objects.get_or_create(zoterokey=key, parent=parent)
                        if created:
                            logger.debug("created new pdf attachement!")
                    attachment.file = new_obj
                    logger.debug(f"adding tags")
                    for t in tags:
                        attachment.tags.append(t)
                    #attachment.parent = Publication.objects.get_or_create(zoterokey=parentItem)
                    new_obj.save()
                    attachment.save()
                    cnt += 1

            else:
                print(f"not importing: {ct}")
        return cnt

    def createCreators(self,creators):
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

    def createArchive(self,data):
        archive = data["archive"]
        location = data["archiveLocation"]

        if archive.strip() == "":
            return None

        location_obj,created = Place.objects.get_or_create(name = location)
        archive,created = Archive.objects.get_or_create(name = archive, location = location_obj)
        return archive

    def createTags(self,tags):
        ret = []
        for tag in tags:
            tag,created = Tag.objects.get_or_create(name = tag["tag"])
            ret.append(tag)
        return ret


    def createPlace(self,place):
        if place:
            place,created = Place.objects.get_or_create(name=place)
            return place
        return None

    def import_bibl_items(self,items, max_no_import= None):
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
                creators = self.createCreators(data["creators"])
                archive = self.createArchive(data)

                place = self.createPlace(data.get("place",""))
                # month,year = self.getMonth_Year(data["date"])
                tags = self.createTags(data["tags"])

                attribs = dict(
                    type_id=types[typ],
                    #citekey=data['key'],
                    title=data['title'],
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
                    dateModified = data["dateModified"],
                    place = place,

                )


                try:
                    obj = publication.Publication.objects.get(zoterokey=key)
                except publication.Publication.DoesNotExist:
                    obj = publication.Publication(zoterokey=key)

                for k,v in attribs.items():
                    setattr(obj,k,v)

                obj.save()

                obj.tags.clear()
                for tag in self.createTags(data.get("tags",[])):
                    obj.tags.add(tag)

                obj.creators.clear()
                for creator in creators:
                    obj.creators.add(creator)

                obj.collection_set.clear()
                for c in data["collections"]:
                    collection,created = Collection.objects.get_or_create(zoterokey = c)
                    collection.items.add(obj)
                    collection.save()
                cnt +=1


            elif typ == "attachment":
                pass # will deal later
            else:
                self.stdout.write(f"{typ} not in types, not imported!")
        return cnt


    def import_collectionMetadata(self,zot):
        collections = zot.collections()
        cnt = 0
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
            cnt += 1
        return cnt


    def add_arguments(self, parser):
        parser.add_argument('library_id',  type=str)
        parser.add_argument('api_key', type=str)
        parser.add_argument("--parent_key_as_filename",default=False,const=True,nargs="?",help="if set then the filenames of the attachment will be the keys of the parent.")
        parser.add_argument("--attachment_key_as_filename", default=False, const=True, nargs="?",
                            help="if set then the filenames of the attachment will be the keys of the attachment.")
        parser.add_argument("--always_upload",default=False,const=True,nargs="?",help="always upload the file, normally checks if file with same sha already exists.")
        parser.add_argument("--check_only_filename", default=False, const=True, nargs="?",
                        help="don't check sha1 just the filename for existance of a file.")
        parser.add_argument("--from_file", default=None, help="filename, load file instead of getting docs from zoter server")
        parser.add_argument("--from_folder", default=None,
                            help="folder where downloaded pdfs with key.pdf as name are already stored.")
        parser.add_argument("--to_file", default=None,
                            help="filename, store file after loading data from zoter server, import with from file")
        parser.add_argument("--only_attachments", default=False,
                            const=True,nargs="?",
                            help="import only attachments")
        parser.add_argument("--no_attachments", default=False,
                            const=True, nargs="?",
                            help="import no attachments")

        parser.add_argument("--no_upload", default=False,
                            const=True, nargs="?",
                            help="add attachment but no file upload")

        parser.add_argument("--max_no_import", default=None, type=int)
        parser.add_argument("--import_collection", default=None)

    def handle(self, *args, **options):

        logging.basicConfig(level=logging.DEBUG)
        library_id = options["library_id"]
        api_key = options["api_key"]
        parent_key_as_filename = options["parent_key_as_filename"]
        attachment_key_as_filename = options["attachment_key_as_filename"]
        overwrite = options["always_upload"]
        check_only_filename = options["check_only_filename"]
        from_file = options["from_file"]
        to_file = options["to_file"]
        only_attachments = options["only_attachments"]
        zot = zotero.Zotero(library_id,"group",api_key)


        if parent_key_as_filename and attachment_key_as_filename:
            print("error you cannot set both patent_key and attachment_key!")
            return
        if from_file:
            import pickle
            with open(from_file,"rb") as inf:
                items = pickle.load(inf)
        else:
            if options["max_no_import"]:
                items = list(zot.items())[0:options["max_no_import"]]
            else:

                if options["import_collection"]:
                    items =  zot.everything(zot.collection_items(options["import_collection"]))
                else:
                    items = zot.everything(zot.items())

        if to_file:
            import pickle
            with open(to_file, "wb") as outf:
                pickle.dump(items,outf)

        if not only_attachments:
            imported = self.import_bibl_items(items)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} bibliographic items!'))
        else:
            self.stdout.write(f'Only attachments will be imported')

        #self.import_notes(items)

        if not options["no_attachments"]:
            imported = self.import_attachment(zot, items, parent_id_as_fn=parent_key_as_filename,
                                              attachment_id_as_fn=attachment_key_as_filename,
                                   always_upload=overwrite,
                                   check_only_filename=check_only_filename,
                                              no_upload=options["no_upload"],
                                              in_folder = options["from_folder"]
                                            )

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} attachments!'))
        imported = self.import_collectionMetadata(zot)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} collections!'))

