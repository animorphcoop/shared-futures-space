# pyre-strict

from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.urls import reverse
from uuid import UUID

from typing import Dict, Any

from .models import Poll, Vote

class PollView(TemplateView):
    def post(self, request: WSGIRequest, uuid: UUID) -> HttpResponseRedirect:
        poll = Poll.objects.get(uuid = uuid)
        if request.user.is_active and 'choice' in request.POST and not poll.check_closed():
            try:
                choice = poll.options.index(request.POST['choice']) + 1
            except ValueError:
                choice = 0
            [v.delete() for v in Vote.objects.filter(poll = poll, user = request.user)] # remove previous vote if there is one
            Vote.objects.create(poll = poll, user = request.user, choice = choice)
            poll.check_closed()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    def get_context_data(self, uuid: UUID, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        poll = Poll.objects.get(uuid = uuid)
        votes = Vote.objects.filter(poll = poll)
        ctx['poll_name'] = poll.question
        ctx['poll_results'] = poll.current_results
        ctx['poll_closed'] = poll.check_closed()
        ctx['poll_expires'] = poll.expires
        return ctx

class PollCreateView(CreateView): # pyre-ignore[24]
    model = Poll
    fields = ['question', 'options', 'expires', 'project']
    def get_success_url(self) -> str:
        return reverse('poll_view', args=[self.object.uuid]) # pyre-ignore[16]
