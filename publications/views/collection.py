from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from publications.models import Publication
from publications.models.collection import Collection

from publications.tables.CollectionTables import CollectionTable, CollectionFilter, CollectionListTable, \
    CollectionAttachmentTable


def collectionsList(request):
    collections = Collection.objects.all()

    table = CollectionListTable(collections)
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    table.order_by = request.GET.get("sort","title")

    return render(request, "collection/collectionList.html", {
        "table": table,
    })

def collectionView(request,pk=None):

    if not pk:
        publications = Publication.objects.all()
        title = "All publications"
        pk = None
        counts = None
    else:
        collection = get_object_or_404(Collection,pk=pk)
        publications = collection.items.all()
        title = collection.name
        pk = collection.pk
        counts = collection.getCounts()

    res = {x : y for x,y in request.GET.items()}
    #has_pdf = res["pdf"]
    res["pdf"] = "unknown"

    filter = CollectionFilter(res, queryset=publications)
    table = CollectionTable(filter.qs)
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    table.order_by = request.GET.get("sort","title")

    attachment_table = CollectionAttachmentTable(collection.collectionattachment_set.all())
    attachment_table.order_by = "-created_at"

    return render(request, "collection/collection.html", {
        "title" : title,
        "pk" : pk,
        "table": table,
        "filter" : filter,
        "counts" : counts,
        "attachment_table" :  attachment_table
    })

def duplicateCollection(request,pk,newName=None):

    newName = request.GET.get("newName", newName)
    collection = get_object_or_404(Collection, pk=pk)
    if not newName:
        return render(request, "collection/duplicateCollection.html", {
            "collection_old": collection.name,
        })

    newCollection = Collection(name=newName,user = request.user)
    newCollection.save()
    for item in collection.items.all():
        newCollection.items.add(item)
    newCollection.save()

    return redirect(newCollection.get_absolute_url())

def collectionTimeDistribution(request,collection):

    only_year = request.GET.get("only_year","false").lower()

    only_year = (only_year == "true")
    collection = get_object_or_404(Collection,pk=collection)

    counter = collection.timeDistribution(only_year)
    ret = []
    if only_year:
        for k,v in counter.items():
            ret.append(f"{k}\t{v}")
    else:
        for y_m,v in counter.items():
            y,m = y_m
            ret.append(f"{y}\t{m}\t{v}")

    ret = "\n".join(ret)

    return HttpResponse(ret.encode("utf-8"),content_type="text/tab-separated-values")



