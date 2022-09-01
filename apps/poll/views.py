# pyre-strict

from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from uuid import UUID

from typing import Dict, Any

from .models import Poll, Vote

class PollView(TemplateView):
    def post(self, request: WSGIRequest, uuid: UUID) -> HttpResponseRedirect:
        if request.user.is_active and 'choice' in request.POST:
            poll = Poll.objects.get(uuid = uuid)
            try:
                choice = poll.options.index(request.POST['choice']) + 1
            except ValueError:
                choice = 0
            [v.delete() for v in Vote.objects.filter(poll = poll, user = request.user)] # remove previous vote if there is one
            Vote.objects.create(poll = poll, user = request.user, choice = choice)
        return HttpResponseRedirect(reverse('poll_view', args=[uuid]))
    def get_context_data(self, uuid: UUID, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        poll = Poll.objects.get(uuid = uuid)
        votes = Vote.objects.filter(poll = poll)
        results = {poll.options[n-1] if n != 0 else 'poll is wrong':[] for n in range(len(poll.options) + 1)}
        for vote in votes:
            results[poll.options[vote.choice - 1] if vote.choice != 0 else 'poll is wrong'].append(vote.user)
        ctx['poll_name'] = poll.question
        ctx['poll_results'] = results
        return ctx
        
