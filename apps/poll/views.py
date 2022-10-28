# pyre-strict

from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.urls import reverse
from django.forms import ChoiceField, ModelChoiceField, ModelForm
from uuid import UUID

from typing import Dict, Any

from .models import BasePoll, SingleChoicePoll, MultipleChoicePoll, BaseVote, SingleVote, MultipleVote
from river.models import River, RiverMembership # pyre-ignore[21]

class PollView(TemplateView):
    def post(self, request: WSGIRequest, uuid: UUID) -> HttpResponseRedirect:
        poll = BasePoll.objects.get(uuid = uuid)
        if hasattr(poll, 'multiplechoicepoll'):
            poll = poll.multiplechoicepoll
        elif hasattr(poll, 'singlechoicepoll'):
            poll = poll.singlechoicepoll
        if request.user.is_active and not poll.check_closed() and 'choice' in request.POST and BaseVote.objects.filter(user = request.user, poll = poll).exists():
            try:
                choice = poll.options.index(request.POST['choice']) + 1
            except ValueError:
                choice = 0
            if hasattr(poll, 'multiplechoicepoll'):
                v = MultipleVote.objects.get(poll = poll, user = request.user)
                if choice in v.choice:
                    v.choice.remove(choice)
                else:
                    v.choice.append(choice)
                v.save()
            elif hasattr(poll, 'singlechoicepoll'):
                SingleVote.objects.filter(poll = poll, user = request.user).update(choice = choice)
            poll.check_closed()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    def get_context_data(self, uuid: UUID, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        ctx = super().get_context_data(**kwargs)
        poll = BasePoll.objects.get(uuid = uuid)
        if hasattr(poll, 'multiplechoicepoll'):
            poll = poll.multiplechoicepoll
        elif hasattr(poll, 'singlechoicepoll'):
            poll = poll.singlechoicepoll
        votes = BaseVote.objects.filter(poll = poll)
        ctx['poll_name'] = poll.question
        ctx['poll_results'] = poll.current_results
        ctx['poll_closed'] = poll.check_closed()
        ctx['poll_expires'] = poll.expires
        return ctx

class PollCreateForm(ModelForm):
    river = ModelChoiceField(queryset=River.objects.all()) # should only be projects you're a member of
    kind = ChoiceField(choices = [('SINGLE', 'single-choice'), ('MULTIPLE', 'multiple-choice')])
    class Meta:
        model = SingleChoicePoll
        fields = ['question', 'options', 'expires']

class PollCreateView(CreateView): # pyre-ignore[24]
    model = SingleChoicePoll
    form_class = PollCreateForm
    def form_valid(self, form) -> HttpResponseRedirect: # pyre-ignore[2] - the type of the form argument is some weird private thing that i can't seem to get hold of
        if form.cleaned_data['kind'] == 'SINGLE':
            new_poll = SingleChoicePoll.objects.create(question = form.instance.question, options = form.instance.options, expires = form.instance.expires)
        elif form.cleaned_data['kind'] == 'MULTIPLE':
            new_poll = MultipleChoicePoll.objects.create(question = form.instance.question, options = form.instance.options, expires = form.instance.expires)
        new_poll.make_votes(form.cleaned_data['river'])
        return HttpResponseRedirect(reverse('poll_view', args=[new_poll.uuid]))
    def get_success_url(self) -> str:
        return reverse('poll_view', args=[self.object.uuid]) # pyre-ignore[16]
