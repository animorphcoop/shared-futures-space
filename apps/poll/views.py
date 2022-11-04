# pyre-strict

from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.urls import reverse
from django.forms import ChoiceField, ModelChoiceField, ModelForm
from uuid import UUID
from itertools import chain

from typing import Dict, Any, List, Tuple

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
        ctx['poll'] = poll
        ctx['poll_name'] = poll.question
        ctx['poll_results'] = poll.current_results
        ctx['poll_closed'] = poll.check_closed()
        ctx['poll_expires'] = poll.expires
        ctx['poll_total_votes'] = len(BaseVote.objects.filter(poll = poll))
        ctx['poll_votes_cast'] = len(list(chain(*ctx['poll_results'].values())))
        ctx['poll_results_winners'] = get_winners(list(poll.current_results.items()))
        return ctx

def get_winners(options: List[Tuple[str,List[Any]]], winners: List[Tuple[str,List[Any]]] = []) -> List[str]: # pyre-ignore[2] Any is actually CustomUser, but for some reason we can't get hold of that
    # get a list of equally-most-highly voted results, in case of a draw
    if len(options) == 0:
        return list(map(lambda pair: pair[0], winners))
    else:
        current_max = len(winners[0][1]) if len(winners) > 0 else 0
        if len(options[0][1]) > current_max:
           return get_winners(options[1:], [options[0]])
        elif len(options[0][1]) == current_max:
            return get_winners(options[1:], winners + [options[0]])
        else:
            return get_winners(options[1:], winners)

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
            new_poll = SingleChoicePoll.objects.create(question = form.instance.question, options = form.instance.options, expires = form.instance.expires, created_by = self.request.user, river = form.cleaned_data['river'])
        elif form.cleaned_data['kind'] == 'MULTIPLE':
            new_poll = MultipleChoicePoll.objects.create(question = form.instance.question, options = form.instance.options, expires = form.instance.expires, created_by = self.request.user, river = form.cleaned_data['river'])
        return HttpResponseRedirect(reverse('poll_view', args=[new_poll.uuid]))
    def get_success_url(self) -> str:
        return reverse('poll_view', args=[self.object.uuid]) # pyre-ignore[16]
