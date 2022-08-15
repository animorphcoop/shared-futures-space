from .models import Tag
from django.shortcuts import render
from django.http import HttpResponse

def all_tags(request):
    tags = Tag.objects.all()
    context = {'Tags': tags}
    return HttpResponse(tags, status=200)
    #return render(request, 'tags/tags.html', context)

def tag(request, tag_name):
    try:
        tag = Tag.objects.get(name=tag_name)
    except Tag.DoesNotExist:
        return HttpResponse('No Such Tag!', status=404)
    return HttpResponse(tag.name, status=200)
