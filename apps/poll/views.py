# pyre-strict

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest

from .models import Poll, Vote

class PollView(TemplateView):
    def get_context_data(self, uuid, **kwargs):
        ctx = super().get_context_data(**kwargs)
        poll = Poll.objects.get(uuid = uuid)
        votes = Vote.objects.filter(poll = poll)
        results = {poll.options[n-1] if n != 0 else 'poll is wrong':[] for n in range(len(poll.options) + 1)}
        for vote in votes:
            results[vote.choice].append(vote.user)
        ctx['poll_name'] = poll.question
        ctx['poll_results'] = results
        return ctx
        
