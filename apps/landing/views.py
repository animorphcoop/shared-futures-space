# pyre-strict
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from typing import Union


def landing(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return render(request, 'landing/landing.html')
