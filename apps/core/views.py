# pyre-strict
from django.http import HttpResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest

#TODO: Pass context variables to load appropriate nav version with appropriate styles
def check_url_nav(request: WSGIRequest) -> HttpResponse:
    #print(request.META.get('HTTP_REFERER').rsplit('/', 2)[1])
    print(request.META.get('HTTP_REFERER'))
    return render(request, 'partials/nav.html')
