from .models import Resource
from django.shortcuts import render

def resource(request):
    resources = Resource.objects.all()
    context = {'Resources': resources}
    return render(request, 'resources/resources.html', context)
