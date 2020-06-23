from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from filer.models import File as F_File

from publications.models.attachment import CollectionAttachment


def showCollectionAttachment(request,pk):

    obj = get_object_or_404(CollectionAttachment,pk = pk)
    ploturl = None
    if "burst" in obj.type_of_processing.name:
        ploturl = reverse("publicationsExtension:plot_burst",kwargs={"burst_pk" : obj.pk} )


    return render(request,"attachment/collectionAttachment.html",{"obj": obj, "ploturl" : ploturl})


def downloadFile(request,pk):

    file = get_object_or_404(F_File.objects,pk=pk)
    fh = open(file.file.path,"rb")
    return FileResponse(fh)