from publications.models.archive import Archive
from publications.models.attachment import ImageAttachment, PDFAttachment, URLAttachment, Attachment
from publications.models.creator import Creator, Role
from publications.models.tag import Tag

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.contrib import admin
try:
	from django.conf.urls import url
except ImportError:
	from django.conf.urls.defaults import url
from publications.models import CustomLink, CustomFile

import publications.admin_views


class ArchiveInline(admin.StackedInline):
	model = Archive
	extra= 1

class CustomLinkInline(admin.StackedInline):
	model = CustomLink
	extra = 1
	max_num = 5


class CustomFileInline(admin.StackedInline):
	model = CustomFile
	extra = 1
	max_num = 5

class AttachmentInline(admin.StackedInline):
	model = Attachment
	extra = 1
	max_num = 5
	fields = ("tags", "type_of_text", "name", "lang", "user", "file")


class ImageAttachmentInline(admin.StackedInline):
	model = ImageAttachment
	extra = 1
	max_num = 5
	fields = ("tags","type_of_text","name","lang","user","file")


class PDFAttachmentInline(admin.StackedInline):
	model = PDFAttachment
	extra = 1
	max_num = 5
	fields = ("tags", "type_of_text", "name", "lang", "user", "file")


class URLAttachmentInline(admin.StackedInline):
	model = URLAttachment
	extra = 1
	max_num = 5


class RoleInline(admin.StackedInline):
	model = Role
	extra = 1
	max_num = 5

class PersonInline(admin.StackedInline):
	model = Role
	extra = 1
	max_num = 5


#class CreatorsInline(admin.StackedInline):
#	model = Creator
#	extra = 1
#	max_num = 5
#	inlines = [PersonInline,RoleInline],


class PublicationAdmin(admin.ModelAdmin):
	list_display = ('type', 'first_author', 'title', 'type', 'year', 'journal_or_book_title')
	list_display_links = ('title',)
	change_list_template = 'admin/publications/publication_change_list.html'
	search_fields = ('title', 'journal', 'authors', 'keywords', 'year')
	fieldsets = (
		(None, {'fields':
			('type', 'title', 'authors', 'date','year', 'month',"tags","callNumber", "archive")}),
		(None, {'fields':
			('journal', 'book_title', 'publisher', 'place', 'institution', 'volume', 'number', 'pages',"rights")}),
		(None, {'fields':
			('citekey', 'keywords', 'url', 'code', 'pdf', 'doi', 'isbn', 'note', 'external','zoterokey')}),
		(None, {'fields':
			('abstract',)}),
		(None, {'fields':
			('image', 'thumbnail')}),
		(None, {'fields':
			('lists',)}),
	)
	inlines = [ImageAttachmentInline,PDFAttachmentInline,CustomLinkInline,
			   CustomFileInline, AttachmentInline# ,CreatorsInline
			   ]

	def get_urls(self):
		return [
				url(r'^import_bibtex/$', publications.admin_views.import_bibtex,
					name='publications_publication_import_bibtex'),
			] + super(PublicationAdmin, self).get_urls()
