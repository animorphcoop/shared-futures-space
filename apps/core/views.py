from django.http import HttpResponse
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest

def check_url_nav(request: WSGIRequest) -> HttpResponse:
    return render(request, 'partials/nav.html')
