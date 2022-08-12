from django.core.handlers.wsgi import WSGIRequest

from .models import Resource
from django.shortcuts import render

def resource(request: WSGIRequest):
    resources = Resource.objects.all()
    context = {'resources': resources}
    return render(request, 'resources/resources.html', context)
def resource_search(request: WSGIRequest):
    print('triggering')
    search_text = request.POST.get('search')
    results = Resource.objects.filter(content__icontains=search_text) #TODO: better query needed
    print(results)
    context = {'results': results}

    return render(request, 'resources/partials/search-results.html', context)