from django.core.handlers.wsgi import WSGIRequest

from .models import Resource
from django.shortcuts import render

def resource(request: WSGIRequest):
    resources = Resource.objects.all()
    context = {'Resources': resources}
    return render(request, 'resources/resources.html', context)
def resource_search(request: WSGIRequest) -> None:
    print('searching')