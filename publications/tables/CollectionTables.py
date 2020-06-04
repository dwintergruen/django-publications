import django_tables2 as tables
import django_filters

from publications.models import Publication


class CollectionFilter(django_filters.FilterSet):

    title = django_filters.CharFilter(lookup_expr="contains")
    date = django_filters.CharFilter(lookup_expr="contains")
    #pdf =  django_filters.BooleanFilter()


    class Meta:
        model = Publication
        fields = ["title","date"]

class CollectionTable(tables.Table):

    pdf = tables.BooleanColumn()

    def render_pdf(self,value,record):
        pdfs = record.pdfattachment_set.count()
        if pdfs>0:
            return True
        return False

    class Meta:
        model = Publication
        template_name = "django_tables2/bootstrap.html"
        fields = ("title","year","date")


