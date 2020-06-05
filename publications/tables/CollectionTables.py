import django_tables2 as tables
import django_filters
from django.urls import reverse
from django.utils.html import format_html

from publications.models import Publication
from publications.models.attachment import Attachment
from publications.models.collection import Collection


class CollectionFilter(django_filters.FilterSet):

    title = django_filters.CharFilter(lookup_expr="contains")
    #date = django_filters.CharFilter(lookup_expr="contains")
    year = django_filters.NumericRangeFilter()
    has_pdf =  django_filters.BooleanFilter(label="has_pdf")


    class Meta:
        model = Publication
        fields = ["title","year",
                  "has_pdf","has_abstract_modified","has_abstract",
                  "has_body","has_html","has_pdf_text"]

class CollectionTable(tables.Table):

    pdf = tables.BooleanColumn()
    atm = tables.Column(empty_values=())
    #url = tables.Column()

    abstract_modified = tables.Column(empty_values=())
    abstract = tables.Column(empty_values=())


    def render_atm(self,value,record):
        atms = record.attachment_set.all()
        types = []
        for atm in atms:
            if atm.type is not None:
                types.append(atm.type.name)
        return format_html("\n".join(types))

    def render_pdf(self, value, record):
        pdfs = record.pdfattachment_set.count()
        if pdfs > 0:
            return True
        return False

    def render_title(self,value,record):
        url = reverse("publicationsExtension:publicationView", kwargs={"pk": record.pk})
        return format_html(f"<a href='{url}'>{value}</a>")

    def render_abstract(self,value,record):
        attachments = Attachment.objects.filter(parent=record)
        for atm in attachments:
            if "type" == "abstract":
                return atm.file.file.read().decode("utf-8")
        return "--"

    def render_abstract_modified(self,value,record):
        attachments = Attachment.objects.filter(parent=record)
        for atm in attachments:
            if atm.type.name == "abstract_modified":
                return atm.file.file.read().decode("utf-8")
        return "--"


    class Meta:
            model = Publication
            template_name = "django_tables2/bootstrap.html"
            fields = ("title","year","date", "abstract",
                      "has_pdf", "has_abstract_modified", "has_abstract",
                      "has_body", "has_html", "has_pdf_text")


class CollectionListTable(tables.Table):

    def render_name(self, value, record):
        url = reverse("publications:collectionView",kwargs={"pk":record.pk})
        return format_html(f"<a href='{url}'>{value}</a>")

    class Meta:
        model = Collection
        template_name = "django_tables2/bootstrap.html"
        fields = ("name",)



