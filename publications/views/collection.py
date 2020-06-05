from django.shortcuts import get_object_or_404, render, redirect

from publications.models import Publication
from publications.models.collection import Collection

from publications.tables.CollectionTables import CollectionTable, CollectionFilter, CollectionListTable


def collectionsList(request):
    collections = Collection.objects.all()


    table = CollectionListTable(collections)
    table.paginate(page=request.GET.get("page", 1), per_page=25)
    table.order_by = "title"  # request.GET.get("sort","title")

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
    table.order_by = "title" #request.GET.get("sort","title")


    return render(request, "collection/collection.html", {
        "title" : title,
        "pk" : pk,
        "table": table,
        "filter" : filter,
        "counts" : counts
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
