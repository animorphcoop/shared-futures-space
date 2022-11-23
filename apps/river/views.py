# pyre-strict

from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.decorators import login_required
from django.db.models.fields import CharField
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.urls import reverse, reverse_lazy
from itertools import chain
from django.db.models import Q

from .forms import CreateRiverForm, RiverChatForm
from .models import River, RiverMembership
from messaging.models import Chat, Message  # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair  # pyre-ignore[21]
from messaging.views import ChatView  # pyre-ignore[21]
from action.util import send_offer  # pyre-ignore[21]
from action.models import Action  # pyre-ignore[21]
from area.models import Area  # pyre-ignore[21]
from messaging.util import send_system_message  # pyre-ignore[21]
from resources.views import filter_and_cluster_resources  # pyre-ignore[21]
from poll.models import SingleChoicePoll  # pyre-ignore[21]
from core.utils.tags_declusterer import tag_cluster_to_list, objects_tags_cluster_list_overwrite  # pyre-ignore[21]
from resources.models import Resource, CaseStudy, HowTo # pyre-ignore[21]
from typing import Dict, List, Any, Union, Type
from area.models import PostCode


class RiverView(DetailView):  # pyre-ignore[24]
    model = River

    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        if (request.POST['action'] == 'leave'):
            membership = RiverMembership.objects.get(user=request.user, river=river)
            if not membership.starter:  # reject starter's attempting to leave, this is not supported by the interface - you should rescind ownership first, because you won't be allowed to if you're the last starter left. TODO: allow starters to leave as well if they're not the last starter
                membership.delete()
                print(
                    '!!! WARNING C !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                # send_system_message(river.chat, 'left_river', context_river = river, context_user_a = request.user)
        if (request.POST['action'] == 'join'):
            if len(RiverMembership.objects.filter(user=request.user, river=river)) == 0 and request.user.post_code.area == river.area: # pyre-ignore[16]
                RiverMembership.objects.create(user=request.user, river=river, starter=False)
                print(
                    '!!! WARNING D !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                # send_system_message(river.chat, 'joined_river', context_river = river, context_user_a = request.user)
        # TESTING PURPOSES ONLY!! TODO # # # # # # # # # #
        if (request.POST['action'] == 'start_envision'):  #
            river.start_envision()  #
        # # # # # # # # # # # # # # # # # # # # # # # # #
        return super().get(request, slug)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['starters'] = RiverMembership.objects.filter(river=context['object'].pk, starter=True)
        context['user'] = self.request.user
        context['slug'] = self.object.slug #pyre-ignore[16]
        context['members'] = RiverMembership.objects.filter(river=context['object'].pk)
        # wow this is ugly
        context['resources'] = list(dict.fromkeys(chain(*[list(chain(HowTo.objects.filter(Q(tags__name__icontains=tag_a) | Q(tags__name__icontains=tag_b)),
                                                                     CaseStudy.objects.filter(Q(tags__name__icontains=tag_a) | Q(tags__name__icontains=tag_b))))
                                for tag_a in self.object.tags.names() for tag_b in self.object.tags.names() if
                                tag_a != tag_b and tag_a > tag_b]))) # ensure we don't have (tag1, tag2) and (tag2, tag1) searched separately. they would be filtered out by fromkeys but might as well remove earlier on
        print(context['resources'])
        context['object'].tags = tag_cluster_to_list(context['object'].tags)
        return context


class EditRiverView(UpdateView):  # pyre-ignore[24]
    model = River
    fields = ['title', 'description']

    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
        return login_required(super().get)(*args, **kwargs)  # pyre-ignore[6]

    def post(self, request: WSGIRequest, slug: str, **kwargs: Dict[str, Any]) -> HttpResponse:  # pyre-ignore[14]
        river = River.objects.get(slug=slug)
        if (RiverMembership.objects.get(river=river, user=request.user).starter == True):
            if ('abdicate' in request.POST and request.POST['abdicate'] == 'abdicate'):
                starters = RiverMembership.objects.filter(river=river, starter=True)
                if (
                        len(starters) >= 2):  # won't be orphaning the river (TODO: allow rivers to be shut down, in which case they can be orphaned)
                    my_membership = RiverMembership.objects.get(river=river, user=request.user, starter=True)
                    my_membership.starter = False
                    my_membership.save()
                    print(
                        '!!! WARNING E !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                    # send_system_message(river.chat, 'lost_ownership', context_user_a = request.user)
            river.title = request.POST['title']
            river.description = request.POST['description']
            river.save()
        return redirect(reverse('view_river', args=[slug]))

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['starters'] = RiverMembership.objects.filter(river=context['object'], starter=True)
        context['members'] = RiverMembership.objects.filter(river=context['object'].pk)
        context['user'] = self.request.user
        return context


class ManageRiverView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        membership = RiverMembership.objects.get(id=request.POST['membership'])
        # security checks
        if (RiverMembership.objects.get(user=request.user, river=river).starter == True
                and membership.river == River.objects.get(slug=slug)):  # since the form takes any uid
            if (request.POST['action'] == 'offer_starter'):
                if not membership.starter:  # not an starter already
                    send_offer(request.user, membership.user, 'become_starter', param_river=river)
                    #send_system_message(get_userpair(request.user, membership.user).chat,'lost_championship_notification', context_user_a=request.user,context_river=membership.river)
            membership.save() # IMPORTANT: happens here because if membership.save is called after membership.delete, it reinstantiates a new identical membership. spent a while chasing that one.
            if (request.POST['action'] == 'remove_swimmer'):
                if not membership.starter:
                    send_system_message(get_userpair(request.user, membership.user).chat, 'removed_from_river', context_user_a = request.user, context_user_b = membership.user, context_river = river)
                    membership.delete()

        return self.get(request, slug)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        river = River.objects.get(slug=kwargs['slug'])
        context['starters'] = RiverMembership.objects.filter(river=river.pk, starter=True)
        context['members'] = RiverMembership.objects.filter(river=river.pk)
        context['slug'] = kwargs['slug']
        print(context['members'])
        return context


class RiverChatView(ChatView):  # pyre-ignore[11]
    form_class: Type[RiverChatForm] = RiverChatForm

    def get_chat(self, river: River, stage: str, topic: str) -> Chat:  # pyre-ignore[11]
        if stage == 'envision':
            chat = river.envision_stage.chat
        elif stage == 'plan':
            if topic == 'general':
                chat = river.plan_stage.general_chat
            elif topic == 'funding':
                chat = river.plan_stage.funding_chat
            elif topic == 'location':
                chat = river.plan_stage.location_chat
            elif topic == 'dates':
                chat = river.plan_stage.dates_chat
        elif stage == 'act':
            if topic == 'general':
                chat = river.act_stage.general_chat
            elif topic == 'funding':
                chat = river.act_stage.funding_chat
            elif topic == 'location':
                chat = river.act_stage.location_chat
            elif topic == 'dates':
                chat = river.act_stage.dates_chat
        elif stage == 'reflect':
            chat = river.reflect_stage.chat
        return chat  # pyre-ignore[61]

    def post(self, request: WSGIRequest, slug: str, stage: str, topic: str = '') -> HttpResponse:
        river = River.objects.get(slug=slug)
        chat = self.get_chat(river, stage, topic)
        # pyre-ignore[16]
        return super().post(request, chat=chat, url=reverse('river_chat', args=[slug, stage, topic]), members=list(
            map(lambda x: x.user, RiverMembership.objects.filter(river=river))))

    def get_context_data(self, slug: str, stage: str, topic: str) -> Dict[str, Any]:
        river = River.objects.get(slug=slug)

        # pyre-ignore[16]
        ctx = super().get_context_data(chat=self.get_chat(river, stage, topic), url=reverse('river_chat', args=[slug, stage, topic]),
                                       members=list(map(lambda x: x.user, RiverMembership.objects.filter(
                                           river=river))))
        ctx['form'] = RiverChatForm
        ctx['slug'] = slug
        ctx['stage'] = stage
        ctx['topic'] = topic
        return ctx


class CreateEnvisionPollView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        if river.current_stage == River.Stage.ENVISION:
            if river.envision_stage.poll is None:
                if 'description' in request.POST:
                    try:
                        poll = SingleChoicePoll.objects.create(
                            question='is this an acceptable vision?',
                            description=request.POST['description'],
                            options=['yes', 'no'],
                            invalid_option=False, expires=timezone.now() + timezone.timedelta(days=3),
                            river=river)
                        river.envision_stage.poll = poll
                        river.envision_stage.save()
                        #send_system_message(chat=river.envision_stage.chat, kind='poll', context_poll=poll) current poll apppears at the bottom of the chat, not as part of it
                        return HttpResponseRedirect(reverse('poll_view', args=[poll.uuid]))
                    except Exception as e:
                        return HttpResponse('could not create poll, unknown error: ' + str(e))
                else:
                    return HttpResponse('could not create poll, no description supplied')
            else:
                return HttpResponse('could not create poll, another poll is still not closed')
        else:
            return HttpResponse('could not create poll, envision stage is finished')

    def get_context_data(self, slug: str) -> Dict[str, Any]:  # pyre-ignore[14]
        ctx = super().get_context_data()
        ctx['river'] = River.objects.get(slug=slug)
        return ctx


class EnvisionView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        River.objects.get(slug=slug).start_plan()  # TODO TESTING PURPOSES ONLY
        return super().get(request, slug)

    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['river'] = River.objects.get(slug=self.kwargs['slug'])
        ctx['owners'] = RiverMembership.objects.filter(river=ctx['river']).values_list('user', flat=True)
        return ctx


class PlanView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        River.objects.get(slug=slug).start_act()  # TODO TESTING PURPOSES ONLY
        return super().get(request, slug)

    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['river'] = River.objects.get(slug=self.kwargs['slug'])
        return ctx


class ActView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        River.objects.get(slug=slug).start_reflect()  # TODO TESTING PURPOSES ONLY
        return super().get(request, slug)

    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['river'] = River.objects.get(slug=self.kwargs['slug'])
        return ctx


class ReflectView(TemplateView):
    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['river'] = River.objects.get(slug=self.kwargs['slug'])
        return ctx


class RiverStartView(CreateView):  # pyre-ignore[24]
    form_class = CreateRiverForm

    def form_valid(self, form) -> HttpResponse: # pyre-ignore[2]
        r = super(RiverStartView, self).form_valid(form)
        for tag in form.cleaned_data['tags']:
            self.object.tags.add(tag) # pyre-ignore[16]
        try:
            post_code = PostCode.objects.all().filter(code=self.request.user.post_code)[0] # pyre-ignore[16]
            self.object.area = post_code.area

        except PostCode.DoesNotExist:

            pass

        self.object.save() # pyre-ignore[16]
        self.object.start_envision() # pyre-ignore[16]

        return r


    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        tags = []
        resources = Resource.objects.all()

        for resource in resources:
            for tag in resource.tags.names():
                if tag.lower() not in tags:
                    tags.append(tag.lower())

        tags.sort()
        context['tags'] = tags
        return context

    def get_success_url(self) -> str:
        RiverMembership.objects.create(user=self.request.user, river=self.object, starter=True)
        return reverse_lazy("view_river", args=[self.object.slug])  # pyre-ignore[16]
