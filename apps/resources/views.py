# pyre-strict
from django.http.request import HttpRequest
from django.http import HttpResponse

from .models import Resource, HowTo, CaseStudy
from django.shortcuts import render

def resource(request: HttpRequest) -> HttpResponse:
    resources = HowTo.objects.all()
    for elem in resources:
        tag_list = []
        print(elem)
        if elem.tags:
            print(elem.tags.all())
            print(type(elem.tags.all()))
            for tag in elem.tags.all():
                tag_list.append(tag)
                print(tag)
            elem.tags = tag_list
            print('reassigned')
            print(elem.tags)
    print(resources)
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)

#TODO: search-results template to be merged with list template as they duplicate styles (or export styles)
def resource_search(request: HttpRequest) -> HttpResponse:
    print('searchin')
    search_text = request.POST.get('search')
    results = Resource.objects.filter(content__icontains=search_text) #TODO: better query needed
    context = {'results': results}
    return render(request, 'resources/partials/search-results.html', context)