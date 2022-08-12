# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import Resource
from django.shortcuts import render

def resource(request: HttpRequest) -> HttpResponse:
    resources = Resource.objects.all()
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)

#TODO: search-results template to be merged with list template as they duplicate styles (or export styles)
def resource_search(request: HttpRequest) -> HttpResponse:
    search_text = request.POST.get('search')
    results = Resource.objects.filter(content__icontains=search_text) #TODO: better query needed
    context = {'results': results}
    return render(request, 'resources/partials/search-results.html', context)