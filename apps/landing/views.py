from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, 'landing/landing.html')
