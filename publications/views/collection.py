from django.shortcuts import get_object_or_404, render

from publications.models import Publication



from publications.tables.CollectionTables import CollectionTable, CollectionFilter


def collectionView(request):

    publications = Publication.objects.all()

    res = {x : y for x,y in request.GET.items()}
    #has_pdf = res["pdf"]
    res["pdf"] = "unknown"

    filter = CollectionFilter(res, queryset=publications)
    table = CollectionTable(filter.qs)
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    table.order_by = "title" #request.GET.get("sort","title")

    return render(request, "collection/collection.html", {
        "table": table,
        "filter" : filter
    })

