# pyre-strict

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest

from .models import Poll

def PollView(request: WSGIRequest, uuid: str) -> HttpResponse:
    poll = Poll.objects.get(uuid = uuid)
    print(poll)
