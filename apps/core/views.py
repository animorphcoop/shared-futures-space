from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


def check_url_nav(request: WSGIRequest) -> HttpResponse:
    return render(request, "partials/nav.html")
