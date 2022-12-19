# pyre-strict
from django.shortcuts import render

from django.views.generic.base import TemplateView
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template
from django.utils.text import slugify
from userauth.models import CustomUser  # pyre-ignore[21]
from userauth.util import get_system_user, user_to_slug, slug_to_user, get_userpair  # pyre-ignore[21]
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from typing import Dict, List, Any, Type, Optional

from .models import Chat, Message, Flag
from river.util import get_chat_containing_river  # pyre-ignore[21]
from river.models import RiverMembership, River  # pyre-ignore[21]
from django.core.paginator import Paginator

from .forms import ChatForm
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet


class ChatView(TemplateView):
    # form_class: Type[ChatForm] = ChatForm

    def get(self, request: WSGIRequest, **kwargs: Dict[str, Any]) -> HttpResponse:  # pyre-ignore[14]
        # direct chat section
        if 'user_path' in kwargs:
            user_path = kwargs['user_path']
            other_user = slug_to_user(user_path)

            [user1, user2] = sorted([request.user.uuid, other_user.uuid])  # pyre-ignore[16]
            userpair = get_userpair(CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2))
            members = CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)

            message_list = Message.objects.all().filter(chat=userpair.chat).order_by('timestamp')

            pagination_data = self.paginate_messages(request, message_list)

            context = {
                'other_user': other_user,
                'members': members,
                'system_user': get_system_user(),
                'page_obj': pagination_data['page_obj'],
                'page_number': pagination_data['page_number'],
                'messages_displayed_count': pagination_data['messages_displayed_count'],
                'messages_left_count': pagination_data['messages_left_count'],
                'direct': True,
                'message_post_url': reverse('user_chat', args=[user_path]),
                'unique_id': user_path,
                'chat_open': not userpair.blocked,
            }
        # river chat section
        elif 'slug' in kwargs:
            river = River.objects.get(slug=kwargs['slug'])
            chat = self.get_river_chat(river, kwargs['stage'], kwargs['topic'])  # pyre-ignore[6]
            message_list = Message.objects.all().filter(chat=chat).order_by('timestamp')
            members = list(map(lambda x: x.user, RiverMembership.objects.filter(river=river)))

            pagination_data = self.paginate_messages(request, message_list)

            chat_poll = self.get_river_poll(river, kwargs['stage'], kwargs['topic'])  # pyre-ignore[6]
            stage_ref = {'envision': river.envision_stage, 'plan': river.plan_stage, 'act': river.act_stage,
                         'reflect': river.reflect_stage}[kwargs['stage']]

            context = {
                'river': river,
                'members': members,
                'slug': kwargs['slug'],
                'stage': kwargs['stage'],
                'topic': kwargs['topic'],
                'page_obj': pagination_data['page_obj'],
                'system_user': get_system_user(),

                'page_number': pagination_data['page_number'],
                'messages_displayed_count': pagination_data['messages_displayed_count'],
                'messages_left_count': pagination_data['messages_left_count'],
                'direct': False,
                'message_post_url': reverse('river_chat', args=[kwargs['slug'], kwargs['stage'], kwargs['topic']]),
                'unique_id': kwargs['stage'] + '-' + kwargs['topic'],  # pyre-ignore[58]
                'chat_open': chat_poll == None or not chat_poll.closed or (chat_poll.closed and not chat_poll.passed),
                'stage_ref': stage_ref,
                'poll_possible': True if kwargs['stage'] == 'envision' else (
                    False if kwargs['stage'] == 'reflect' else (kwargs['topic'] != 'general') or (
                            kwargs['topic'] == 'general' and stage_ref.money_poll and stage_ref.money_poll.passed
                            and stage_ref.place_poll and stage_ref.place_poll.passed and stage_ref.time_poll
                            and stage_ref.time_poll.passed)),
                'poll_ref': stage_ref.general_poll if kwargs['stage'] == 'envision' or kwargs['stage'] == 'reflect' else
                {'general': stage_ref.general_poll, 'money': stage_ref.money_poll, 'place': stage_ref.place_poll,
                 'time': stage_ref.time_poll}[kwargs['topic']],
                'chat_ref': stage_ref.general_chat if kwargs['stage'] == 'envision' or kwargs['stage'] == 'reflect' else
                {'general': stage_ref.general_chat, 'money': stage_ref.money_chat, 'place': stage_ref.place_chat,
                 'time': stage_ref.time_chat}[kwargs['topic']],
                'starters': RiverMembership.objects.filter(river=river, starter=True).values_list('user', flat=True),
            }
            if request.user.is_authenticated:
                context['my_flags'] = list(map(lambda f: f.message.uuid, Flag.objects.filter(flagged_by=request.user)))



        else:
            context = {}  # just in case
        if request.GET.get('page'):
            return render(request, 'messaging/message_list.html', context)
        else:
            return render(request, self.template_name, context)

    def post(self, request: WSGIRequest, **kwargs: Dict[str, Any]) -> HttpResponse:
        if 'user_path' in kwargs:
            user_path = kwargs['user_path']
            other_user = slug_to_user(user_path)

            [user1, user2] = sorted([request.user.uuid, other_user.uuid])  # pyre-ignore[16]
            userpair = get_userpair(CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2))

            chat = userpair.chat
            members = [CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)]
            chat_open = not userpair.blocked
            context = {'message_post_url': reverse('user_chat', args=[user_path]), 'unique_id': user_path,
                       'chat_open': chat_open}
        elif 'slug' in kwargs:
            river = River.objects.get(slug=kwargs['slug'])
            members = list(map(lambda x: x.user, RiverMembership.objects.filter(river=river)))
            chat = self.get_river_chat(river, kwargs['stage'], kwargs['topic'])  # pyre-ignore[6]
            chat_poll = self.get_river_poll(river, kwargs['stage'], kwargs['topic'])  # pyre-ignore[6]
            chat_open = chat_poll == None or not chat_poll.closed or (chat_poll.closed and not chat_poll.passed)
            stage_ref = {'envision': river.envision_stage, 'plan': river.plan_stage, 'act': river.act_stage,
                         'reflect': river.reflect_stage}[kwargs['stage']]
            context = {
                'message_post_url': reverse('river_chat', args=[kwargs['slug'], kwargs['stage'], kwargs['topic']]),
                'unique_id': kwargs['stage'] + '-' + kwargs['topic'],  # pyre-ignore[58]
                'chat_open': chat_open, 'stage_ref': stage_ref, 'river': river,
                'poll_possible': True if kwargs['stage'] == 'envision' else (
                    False if kwargs['stage'] == 'reflect' else (kwargs['topic'] != 'general') or (
                            kwargs['topic'] == 'general' and stage_ref.money_poll and stage_ref.money_poll.passed
                            and stage_ref.place_poll and stage_ref.place_poll.passed and stage_ref.time_poll
                            and stage_ref.time_poll.passed)),
                'poll_ref': stage_ref.general_poll if kwargs['stage'] == 'envision' or kwargs['stage'] == 'reflect' else
                {'general': stage_ref.general_poll, 'money': stage_ref.money_poll, 'place': stage_ref.place_poll,
                 'time': stage_ref.time_poll}[kwargs['topic']],
                'chat_ref': stage_ref.general_chat if kwargs['stage'] == 'envision' or kwargs['stage'] == 'reflect' else
                {'general': stage_ref.general_chat, 'money': stage_ref.money_chat, 'place': stage_ref.place_chat,
                 'time': stage_ref.time_chat}[kwargs['topic']],
                'starters': RiverMembership.objects.filter(river=river, starter=True).values_list('user', flat=True), }
        else:
            return HttpResponse('error - no user_path or slug specified')
        if request.user in members:
            if 'text' in request.POST and chat_open:
                chat_form = ChatForm(request.POST, request.FILES)
                if chat_form.is_valid():
                    chat_form.full_clean()
                    context['message'] = Message.objects.create(sender=request.user,
                                                                text=chat_form.cleaned_data.get('text', None),
                                                                image=chat_form.cleaned_data.get('image', None),
                                                                file=chat_form.cleaned_data.get('file', None),
                                                                chat=chat)
                else:
                    return HttpResponse(
                        "<span class='block text-body text-red-important text-center'>Sorry, the file format not supported.</span>")
            if 'flag' in request.POST:
                m = Message.objects.get(uuid=request.POST['flag'])
                m.flagged(request.user)
                context['message'] = m

            if 'starter_hide' in request.POST and RiverMembership.objects.filter(user=request.user, starter=True,
                                                                                 river=get_chat_containing_river(
                                                                                     chat)).exists():
                m = Message.objects.get(uuid=request.POST['starter_hide'])
                m.hidden = not m.hidden
                m.hidden_reason = 'by the river starter'
                m.save()
                context['message'] = m
            context['my_flags'] = list(map(lambda f: f.message.uuid, Flag.objects.filter(flagged_by=request.user)))
        return render(request, 'messaging/user_message_snippet.html', context)

    def paginate_messages(self, request: WSGIRequest, message_list: QuerySet) -> Dict[str, Any]:

        # it is currently impossible to reverse pagnination order https://code.djangoproject.com/ticket/4956
        # but can include orphans: https://docs.djangoproject.com/en/4.1/ref/paginator/#django.core.paginator.Paginator.orphans
        paginator = Paginator(message_list, 10, 9)

        if request.GET.get('page'):
            page_number = request.GET.get('page')
        else:
            page_number = paginator.num_pages

        page_obj = paginator.get_page(page_number)  # pyre-ignore[6]

        total_message_count = message_list.count()

        messages_displayed_count = total_message_count - page_obj.start_index() + 1
        messages_left_count = total_message_count - messages_displayed_count

        pagination_data = {
            'page_obj': page_obj,
            'page_number': page_number,
            'messages_displayed_count': messages_displayed_count,
            'messages_left_count': messages_left_count
        }
        return pagination_data

    def get_river_chat(self, river: River, stage: str, topic: str) -> Chat:  # pyre-ignore[11]
        if stage == 'plan':
            print(river.title)
        if stage == 'envision':
            chat = river.envision_stage.general_chat
        elif stage == 'plan':
            if topic == 'general':
                chat = river.plan_stage.general_chat
            elif topic == 'money':
                chat = river.plan_stage.money_chat
            elif topic == 'place':
                chat = river.plan_stage.place_chat
            elif topic == 'time':
                chat = river.plan_stage.time_chat
        elif stage == 'act':
            if topic == 'general':
                chat = river.act_stage.general_chat
            elif topic == 'money':
                chat = river.act_stage.money_chat
            elif topic == 'place':
                chat = river.act_stage.place_chat
            elif topic == 'time':
                chat = river.act_stage.time_chat
        elif stage == 'reflect':
            chat = river.reflect_stage.general_chat
        return chat  # pyre-ignore[61]

    def get_river_poll(self, river: River, stage: str, topic: str):  # pyre-ignore[3]
        if stage == 'envision':
            poll = river.envision_stage.general_poll
        elif stage == 'plan':
            if topic == 'general':
                poll = river.plan_stage.general_poll
            elif topic == 'money':
                poll = river.plan_stage.money_poll
            elif topic == 'place':
                poll = river.plan_stage.place_poll
            elif topic == 'time':
                poll = river.plan_stage.time_poll
        elif stage == 'act':
            if topic == 'general':
                poll = river.act_stage.general_poll
            elif topic == 'money':
                poll = river.act_stage.money_poll
            elif topic == 'place':
                poll = river.act_stage.place_poll
            elif topic == 'time':
                poll = river.act_stage.time_poll
        elif stage == 'reflect':
            poll = river.reflect_stage.general_poll
        return poll  # pyre-ignore[61]
