# pyre-strict
from django.shortcuts import render

from django.views.generic.base import TemplateView
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template
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


# from userauth.forms import ChatForm


# usage note: you must redefine post and get_context_data
# both need to be passed three kwargs:
#   a list of users called 'members' which is the people allowed to post in the chat
#   a Chat called 'chat'
#   a str called 'url' which is the url to post new chat requests to, ie. if htmx is in use it's the hx-post not the address bar url
# your get_context_data should define user_anonymous_message and not_member_message in context


class ChatView(TemplateView):
    # form_class: Type[ChatForm] = ChatForm

    def get(self, request, **kwargs: Dict[str, Any]):
        for key in kwargs:
            if key == 'user_path':
                print(kwargs['user_path'])
                user_path = kwargs['user_path']
                other_user = slug_to_user(user_path)
                print('here')
                print(request.GET.get('chat'))
                # other_user = slug_to_user(user_path)

                [user1, user2] = sorted([request.user.uuid, other_user.uuid])  # pyre-ignore[16]
                userpair = get_userpair(CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2))
                members = CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)

                message_list = Message.objects.all().filter(chat=userpair.chat).order_by('timestamp')

                paginator = Paginator(message_list, 10)
                if request.GET.get('page'):
                    page_number = request.GET.get('page')
                else:
                    page_number = paginator.num_pages

                page_obj = paginator.get_page(page_number)


                # print(request.GET.get('page'))
                context = {
                    'members': members,
                    'page_obj': page_obj,
                    'page_number': page_number,
                }
                if request.GET.get('page'):
                    return render(request, 'messaging/message_list.html', context)
                else:
                    return render(request, 'userauth/account/user_chat.html', context)
            elif key == 'slug':
                river = River.objects.get(slug=kwargs['slug'])
                print(kwargs['slug'])
                print(kwargs['stage'])
                print(kwargs['topic'])
                chat = self.get_river_chat(river, kwargs['stage'], kwargs['topic'])
                url = reverse('river_chat', args=[kwargs['slug'], kwargs['stage'], kwargs['topic']])
                message_list = Message.objects.all().filter(chat=chat).order_by('timestamp')

                members = list(map(lambda x: x.user, RiverMembership.objects.filter(
                    river=river)))

                context = {
                    'members': members

                }

                paginator = Paginator(message_list, 10)
                if request.GET.get('page'):
                    page_number = request.GET.get('page')
                else:
                    page_number = paginator.num_pages

                page_obj = paginator.get_page(page_number)

                context['page_obj'] = page_obj
                context['page_number'] = page_number

            if request.GET.get('page'):
                return render(request, 'messaging/message_list.html', context)
            else:
                return render(request, 'messaging/messages.html', context)

    def post(self, request: WSGIRequest, user_path) -> HttpResponse:

        other_user = slug_to_user(user_path)

        [user1, user2] = sorted([request.user.uuid, other_user.uuid])  # pyre-ignore[16]
        userpair = get_userpair(CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2))

        chat = userpair.chat
        url = reverse('user_chat', args=[other_user])  # pyre-ignore[16]
        members = [CustomUser.objects.get(uuid=user1), CustomUser.objects.get(uuid=user2)]

        if request.user in members:
            if 'text' in request.POST:
                image = request.FILES.get('image', None)
                file = request.FILES.get('file', None)
                if file and image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], image=image, file=file, chat=chat)
                elif image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], image=image, chat=chat)
                elif file and image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], file=file, chat=chat)
                else:
                    new_msg = Message(sender=request.user, text=request.POST['text'], chat=chat)
                new_msg.save()
            if 'flag' in request.POST:
                m = Message.objects.get(uuid=request.POST['flag'])
                m.flagged(request.user)
            if 'starter_hide' in request.POST and RiverMembership.objects.filter(user=request.user, starter=True,
                                                                                 river=get_chat_containing_river(
                                                                                     chat)).exists():
                m = Message.objects.get(uuid=request.POST['starter_hide'])
                m.hidden = not m.hidden
                m.hidden_reason = 'by the river starter'
                m.save()
            # return super().get(request)
            return render(request, 'messaging/user_message_snippet.html', {'message': new_msg})
        else:
            if 'retrieve_messages' in request.POST:
                return HttpResponse(get_template('messaging/messages_snippet.html').render({}))
            else:
                return super().get(request)

    def get_river_chat(self, river: River, stage: str, topic: str) -> Chat:  # pyre-ignore[11]
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


'''
class ChatView(TemplateView):
    template_name = 'messaging/messages_snippet.html'


    def get_context_data(self, **kwargs: Dict[str, Any], ) -> Dict[str, Any]:
        print(kwargs['user_path'])
        context = super().get_context_data(**kwargs)

        msg_from, msg_no = 0, 10  # how many messages back to begin, and how many to retrieve
        if ('from' in self.request.GET and self.request.GET['from'].isdigit()):
            msg_from = int(self.request.GET['from'])
        if ('interval' in self.request.GET and self.request.GET['interval'].isdigit()):
            msg_no = int(self.request.GET['interval'])
        messages = Message.objects.filter(chat=kwargs['chat']).order_by('timestamp')
        # context['user_anonymous_message'] = 'Please log in to participate'
        # context['not_member_message'] = 'Join the river to get involved in the conversation!'
        context['messages'] = messages[max(0, len(messages) - (msg_no + msg_from)): len(messages) - msg_from]
        # context['more_back'] = msg_no + msg_from < len(messages)
        # context['interval'] = msg_no
        context['from'] = msg_from
        # context['back_from'] = int(min(msg_from + (msg_no / 2), len(messages)))
        # context['forward_from'] = int(max(msg_from - (msg_no / 2), 0))
        context['members'] = kwargs['members']
        context['system_user'] = get_system_user()
        return context

    def get_messages(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for key in context:
            print(key)

        if 'retrieve_messages' in self.request.GET:
            print('HERE')
            msg_from, msg_no = 0, 10  # how many messages back to begin, and how many to retrieved
            if ('from' in self.request.GET and self.request.GET['from'].isdigit()):
                msg_from = int(self.request.POST['from'])
            if ('interval' in self.request.GET and self.request.GET['interval'].isdigit()):
                msg_no = int(self.request.POST['interval'])
            messages = Message.objects.filter(chat=context['chat']).order_by('timestamp')
            context['messages'] = messages[
                                  max(0, len(messages) - (msg_no + msg_from)): max(0, len(messages) - msg_from)]
            context['user'] = self.request.user
            context['from'] = msg_from
            context['more_back'] = msg_no + msg_from < len(messages)
            return context
        else:
            print('NEONE')
            return context


    def post(self, request: WSGIRequest, chat: Chat, members: List[CustomUser],
             # pyre-ignore[11] - says CustomUser isn't defined as a type?
             url: str) -> HttpResponse:
        if request.user in members:
            if 'text' in request.POST:
                image = request.FILES.get('image', None)
                file = request.FILES.get('file', None)
                if file and image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], image=image, file=file, chat=chat)
                elif image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], image=image, chat=chat)
                elif file and image:
                    new_msg = Message(sender=request.user, text=request.POST['text'], file=file, chat=chat)
                else:
                    new_msg = Message(sender=request.user, text=request.POST['text'], chat=chat)
                new_msg.save()
            if 'flag' in request.POST:
                m = Message.objects.get(uuid=request.POST['flag'])
                m.flagged(request.user)
            if 'starter_hide' in request.POST and RiverMembership.objects.filter(user=request.user, starter=True,
                                                                                 river=get_chat_containing_river(
                                                                                     chat)).exists():
                m = Message.objects.get(uuid=request.POST['starter_hide'])
                m.hidden = not m.hidden
                m.hidden_reason = 'by the river starter'
                m.save()
        else:
            if 'retrieve_messages' in request.POST:
                return HttpResponse(get_template('messaging/messages_snippet.html').render({}))
            else:
                return super().get(request)
'''
