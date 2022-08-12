from .models import Tag
from django.shortcuts import render

def tag(request):
    tags = Tags.objects.all()
    context = {'Tags': tags}
    return render(request, 'tags/tags.html', context)
