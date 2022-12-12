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


# TODO: Rewrite when we settle on how it works now
# usage note: you must redefine post and get_context_data
# both need to be passed three kwargs:
#   a list of users called 'members' which is the people allowed to post in the chat
#   a Chat called 'chat'
#   a str called 'url' which is the url to post new chat requests to, ie. if htmx is in use it's the hx-post not the address bar url
# your get_context_data should define user_anonymous_message and not_member_message in context


class ChatView(TemplateView):
    # form_class: Type[ChatForm] = ChatForm
    
    def get(self, request: WSGIRequest, **kwargs: Dict[str, Any]) -> HttpResponse: # pyre-ignore[14]
        # direct chat section
        if'user_path' in kwargs:
            user_path = kwargs['user_path']
            other_user = slug_to_user(user_path)

            [user1, user2] = sorted([request.user.uuid, other_user.uuid]) # pyre-ignore[16]
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
                'chat_open': True,
            }
        # river chat section
        elif 'slug' in kwargs:
            river = River.objects.get(slug=kwargs['slug'])
            chat = self.get_river_chat(river, kwargs['stage'], kwargs['topic']) # pyre-ignore[6]
            message_list = Message.objects.all().filter(chat=chat).order_by('timestamp')
            members = list(map(lambda x: x.user, RiverMembership.objects.filter(river=river)))

            pagination_data = self.paginate_messages(request, message_list)

            chat_poll = self.get_river_poll(river, kwargs['stage'], kwargs['topic'])

            context = {
                'members': members,
                'slug': kwargs['slug'],
                'stage': kwargs['stage'],
                'topic': kwargs['topic'],
                'page_obj': pagination_data['page_obj'],
                'page_number': pagination_data['page_number'],
                'messages_displayed_count': pagination_data['messages_displayed_count'],
                'messages_left_count': pagination_data['messages_left_count'],
                'direct': False,
                'message_post_url': reverse('river_chat', args=[kwargs['slug'], kwargs['stage'], kwargs['topic']]),
                'unique_id': kwargs['stage'] + '-' + kwargs['topic'], # pyre-ignore[58]
                'chat_open': chat_poll == None or not chat_poll.closed,
            }
        else:
            context = {} # just in case
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
            context = {'message_post_url': reverse('user_chat', args=[user_path]), 'unique_id': user_path, 'chat_open': True}
        elif 'slug' in kwargs:
            river = River.objects.get(slug=kwargs['slug'])
            members = list(map(lambda x: x.user, RiverMembership.objects.filter(river=river)))
            chat = self.get_river_chat(river, kwargs['stage'], kwargs['topic']) # pyre-ignore[6]
            chat_poll = self.get_river_poll(river, kwargs['stage'], kwargs['topic'])
            context = {'message_post_url': reverse('river_chat', args=[kwargs['slug'], kwargs['stage'], kwargs['topic']]), 'unique_id': kwargs['stage'] + '-' + kwargs['topic'], # pyre-ignore[58]
                       'chat_open': chat_poll == None or not chat_poll.closed,}
        else:
            return HttpResponse('error - no user_path or slug specified')
        if request.user in members:
            if 'text' in request.POST:
                chat_form = ChatForm(request.POST, request.FILES)
                if chat_form.is_valid():
                    chat_form.full_clean()
                    context['message'] = Message.objects.create(sender = request.user, text = chat_form.cleaned_data.get('text', None),
                                                            image = chat_form.cleaned_data.get('image', None),
                                                            file = chat_form.cleaned_data.get('file', None), chat = chat)
                else:
                    return HttpResponse("<span class='block text-body text-red-important text-center'>Sorry, the file format not supported.</span>")
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
            context['my_flags'] = list(map(lambda f: f.message.uuid, Flag.objects.filter(flagged_by = request.user))) # pyre-ignore[6]
        return render(request, 'messaging/user_message_snippet.html', context)

    def paginate_messages(self, request: WSGIRequest, message_list: QuerySet) -> Dict[str, Any]:

        # it is currently impossible to reverse pagnination order https://code.djangoproject.com/ticket/4956
        # but can include orphans: https://docs.djangoproject.com/en/4.1/ref/paginator/#django.core.paginator.Paginator.orphans
        paginator = Paginator(message_list, 10, 9)

        if request.GET.get('page'):
            page_number = request.GET.get('page')
        else:
            page_number = paginator.num_pages

        page_obj = paginator.get_page(page_number) # pyre-ignore[6]

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
        if stage == 'envision':
            chat = river.envision_stage.general_chat
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
            chat = river.reflect_stage.general_chat
        return chat  # pyre-ignore[61]

    def get_river_poll(self, river: River, stage: str, topic: str):
        if stage == 'envision':
            poll = river.envision_stage.general_poll
        elif stage == 'plan':
            if topic == 'general':
                poll = river.plan_stage.general_poll
            elif topic == 'funding':
                poll = river.plan_stage.funding_poll
            elif topic == 'location':
                poll = river.plan_stage.location_poll
            elif topic == 'dates':
                poll = river.plan_stage.dates_poll
        elif stage == 'act':
            if topic == 'general':
                poll = river.act_stage.general_poll
            elif topic == 'funding':
                poll = river.act_stage.funding_poll
            elif topic == 'location':
                poll = river.act_stage.location_poll
            elif topic == 'dates':
                poll = river.act_stage.dates_poll
        return poll  # pyre-ignore[61]




