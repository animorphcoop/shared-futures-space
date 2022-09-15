# pyre-strict

from django.views.generic.edit import CreateView, _ModelFormT
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.urls import reverse
from django.forms import ModelChoiceField, ModelForm
from uuid import UUID

from typing import Dict, Any

from .models import Poll, Vote
from project.models import Project, ProjectMembership # pyre-ignore[21]

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

class PollCreateForm(ModelForm):
    project = ModelChoiceField(queryset=Project.objects.all()) # should only be projects you're a member of
    class Meta:
        model = Poll
        fields = ['question', 'options', 'expires']

class PollCreateView(CreateView): # pyre-ignore[24]
    model = Poll
    form_class = PollCreateForm
    def form_valid(self, form: _ModelFormT) -> HttpResponseRedirect:
        new_poll = Poll.objects.create(question = form.instance.question, options = form.instance.options, expires = form.instance.expires, voter_num = len(ProjectMembership.objects.filter(project = form.cleaned_data['project'])))
        return HttpResponseRedirect(reverse('poll_view', args=[new_poll.uuid]))
    def get_success_url(self) -> str:
        return reverse('poll_view', args=[self.object.uuid]) # pyre-ignore[16]
