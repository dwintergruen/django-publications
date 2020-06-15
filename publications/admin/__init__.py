from publications.models.archive import Archive
from publications.models.attachment import ImageAttachment, PDFAttachment, Attachment, AttachmentType, \
    CollectionAttachment
from publications.models.collection import Collection
from publications.models.creator import Creator, Person, Role
from publications.models.ner_object import NER_object, NER_type
from publications.models.tag import Tag

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.contrib import admin
from publications.models import Type, List, Publication
from .publicationadmin import PublicationAdmin
from .typeadmin import TypeAdmin
from .listadmin import ListAdmin
from .orderedmodeladmin import OrderedModelAdmin

admin.site.register(Type, TypeAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(Publication,PublicationAdmin)
admin.site.register(Creator)
admin.site.register(Archive)
admin.site.register(Person)
admin.site.register(Role)
admin.site.register(Tag)
admin.site.register(Collection)
admin.site.register(ImageAttachment)
admin.site.register(PDFAttachment)
admin.site.register(Attachment)
admin.site.register(AttachmentType)
admin.site.register(NER_object)
admin.site.register(NER_type)
admin.site.register(CollectionAttachment)







