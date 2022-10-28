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

from .forms import CreateRiverForm
from .models import River, RiverMembership
from messaging.models import Chat, Message  # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair  # pyre-ignore[21]
from messaging.views import ChatView  # pyre-ignore[21]
from action.util import send_offer  # pyre-ignore[21]
from action.models import Action  # pyre-ignore[21]
from area.models import Area  # pyre-ignore[21]
from messaging.util import send_system_message  # pyre-ignore[21]
from resources.views import filter_and_cluster_resources  # pyre-ignore[21]
from poll.models import SingleChoicePoll # pyre-ignore[21]
from core.utils.tags_declusterer import tag_cluster_to_list, objects_tags_cluster_list_overwrite  # pyre-ignore[21]

from typing import Dict, List, Any, Union

class RiverView(DetailView):  # pyre-ignore[24]
    model = River

    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        if (request.POST['action'] == 'leave'):
            membership = RiverMembership.objects.get(user=request.user, river=river)
            if not membership.owner:  # reject owners attempting to leave, this is not supported by the interface - you should rescind ownership first, because you won't be allowed to if you're the last owner left. TODO: allow owners to leave as well if they're not the last owner
                membership.delete()
                print(
                    '!!! WARNING C !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                # send_system_message(river.chat, 'left_river', context_river = river, context_user_a = request.user)
        if (request.POST['action'] == 'join'):
            if len(RiverMembership.objects.filter(user=request.user, river=river)) == 0:
                RiverMembership.objects.create(user=request.user, river=river, owner=False, champion=False)
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
        context['owners'] = RiverMembership.objects.filter(river=context['object'].pk, owner=True)
        context['champions'] = RiverMembership.objects.filter(river=context['object'].pk, champion=True)
        context['members'] = RiverMembership.objects.filter(river=context['object'].pk)
        context['object'].tags = tag_cluster_to_list(context['object'].tags)
        context['resources'] = list(chain(
            *[filter_and_cluster_resources(tag, 'latest') for tag in map(lambda t: t.name, context['object'].tags)]))
        return context


#TODO: Write a helper method for parsing paths if there are whitespaces?
class SpringView(TemplateView):
    def get(self, request: HttpRequest, *args: List[Any], **kwargs: Dict[str, str]) -> Union[
        HttpResponse, HttpResponseRedirect]:
        # RETURN URL PATH
        slug = str(kwargs['slug'])
        if '-' in slug:
            name = slug.replace('-', ' ')
        else:
            name = slug

        if Area.objects.filter(name__iexact=name).exists():
            area = Area.objects.get(name__iexact=name)
        else:
            return HttpResponseRedirect(reverse('404'))

        rivers = River.objects.filter(area=area)
        #rivers = River.objects.all()
        #members = []
        for river in rivers:
            river.tags = tag_cluster_to_list(river.tags)

            river.us = RiverMembership.objects.filter(river=river)
            river.swimmers = RiverMembership.objects.filter(river=river).values_list('user', flat=True)

            #TEMP - comment below
            river.membership = RiverMembership.objects.filter(river=river)
            '''
            for rivermemb in RiverMembership.objects.filter(river=river):
                print(rivermemb.user)
                members.append(rivermemb.user)
            river.members = members
            '''
        num_swimmers = RiverMembership.objects.filter(
            river__in=River.objects.filter(area=area)).values_list('user', flat=True).distinct().count()


        #TODO: Add all members, owner and champions to the context 'river.swimmers' being ints; temp members
        context = {
            'area': area,
            'rivers': rivers,
            'num_swimmers': num_swimmers
        }

        # context is:
        #   'rivers' -> list of rivers with .tags and .swimmers set appropriately
        #   'num_swimmers' -> number of distinct swimmers involved in all rivers in this spring

        return render(request, 'river/all_rivers.html', context)


class EditRiverView(UpdateView):  # pyre-ignore[24]
    model = River
    fields = ['name', 'description']

    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
        return login_required(super().get)(*args, **kwargs)  # pyre-ignore[6]

    def post(self, request: WSGIRequest, slug: str, **kwargs: Dict[str, Any]) -> HttpResponse:  # pyre-ignore[14]
        river = River.objects.get(slug=slug)
        if (RiverMembership.objects.get(river=river, user=request.user).owner == True):
            if ('abdicate' in request.POST and request.POST['abdicate'] == 'abdicate'):
                ownerships = RiverMembership.objects.filter(river=river, owner=True)
                if (
                        len(ownerships) >= 2):  # won't be orphaning the river (TODO: allow rivers to be shut down, in which case they can be orphaned)
                    my_membership = RiverMembership.objects.get(river=river, user=request.user, owner=True)
                    my_membership.owner = False
                    my_membership.save()
                    print(
                        '!!! WARNING E !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                    # send_system_message(river.chat, 'lost_ownership', context_user_a = request.user)
            river.name = request.POST['name']
            river.description = request.POST['description']
            river.save()
        return redirect(reverse('view_river', args=[slug]))

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = RiverMembership.objects.filter(river=context['object'], owner=True)
        return context


class ManageRiverView(DetailView):  # pyre-ignore[24]
    model = River

    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        membership = RiverMembership.objects.get(id=request.POST['membership'])
        # security checks
        if (RiverMembership.objects.get(user=request.user, river=river).owner == True
                and membership.river == River.objects.get(slug=slug)):  # since the form takes any uid
            if (request.POST['action'] == 'offer_ownership'):
                if not membership.owner:  # not an owner already
                    send_offer(request.user, membership.user, 'become_owner', param_river=river)
            elif (request.POST['action'] == 'offer_championship'):
                if not membership.champion:
                    send_offer(request.user, membership.user, 'become_champion', param_river=river)
            elif (request.POST['action'] == 'remove_championship'):
                if membership.champion:
                    membership.champion = False
                    print(
                        '!!! WARNING F !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                    # send_system_message(river.chat, 'lost_championship', context_user_a = membership.user, context_user_b = request.user)
                    send_system_message(get_userpair(request.user, membership.user).chat,
                                        'lost_championship_notification', context_user_a=request.user,
                                        context_river=membership.river)
            membership.save()
        return self.get(request, slug)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ownerships'] = RiverMembership.objects.filter(river=context['object'].pk, owner=True)
        context['memberships'] = RiverMembership.objects.filter(river=context['object'].pk)
        return context


class RiverChatView(ChatView):  # pyre-ignore[11]
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
        return super().post(request, chat=chat, url=request.get_full_path(), members=list(
            map(lambda x: x.user, RiverMembership.objects.filter(river=river))))
    def get_context_data(self, slug: str, stage: str, topic: str) -> Dict[str, Any]:
        river = River.objects.get(slug=slug)
        # pyre-ignore[16]
        ctx = super().get_context_data(chat=self.get_chat(river, stage, topic), url=self.request.get_full_path(),
                                       members=list(map(lambda x: x.user, RiverMembership.objects.filter(
                                           river=river))))
        return ctx

class CreateEnvisionPollView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug = slug)
        if river.current_stage == River.Stage.ENVISION:
            if river.envision_stage.poll is None:
                if 'description' in request.POST:
                    try:
                        poll = SingleChoicePoll.objects.create(question = 'Is this an acceptable vision: "' + request.POST['description'] + '"?', options = ['yes', 'no'],
                                                               invalid_option = False, expires = timezone.now() + timezone.timedelta(days=3))
                        poll.make_votes(river)
                        send_system_message(chat = river.envision_stage.chat, kind = 'poll', context_poll = poll)
                        return HttpResponseRedirect(reverse('view_envision', args=[river.slug]))
                    except Exception as e:
                        return HttpResponse('could not create poll, unknown error: ' + str(e))
                else:
                    return HttpResponse('could not create poll, no description supplied')
            else:
                return HttpResponse('could not create poll, another poll is still not closed')
        else:
            return HttpResponse('could not create poll, envision stage is finished')
    def get_context_data(self, slug: str) -> Dict[str,Any]: # pyre-ignore[14]
        ctx = super().get_context_data()
        ctx['river'] = River.objects.get(slug = slug)
        return ctx


class EnvisionView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        River.objects.get(slug=slug).start_plan()  # TODO TESTING PURPOSES ONLY
        return super().get(request, slug)

    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        ctx = super().get_context_data(*args, **kwargs)
        ctx['river'] = River.objects.get(slug=self.kwargs['slug'])
        ctx['owners'] = RiverMembership.objects.filter(river = ctx['river']).values_list('user', flat=True)
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


class RiverStartView(CreateView): # pyre-ignore[24]
    form_class = CreateRiverForm

    def get_context_data(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        rivers = River.objects.all()
        #rivers = objects_tags_cluster_list_overwrite(River.objects.all())
        tags = []
        for river in rivers:
            for tag in river.tags.all():
                tags.append(tag)
            # print(river.tags.names())
            #single_object_tags_cluster_overwrite
           # tags.append(tag_cluster_to_list(river.tags))
        context['tags'] = tags
        return context

    def get_success_url(self) -> str:
        RiverMembership.objects.create(user=self.request.user, river=self.object, owner=True, champion=False)
        return reverse_lazy("view_river", args=[self.object.slug]) # pyre-ignore[16]
