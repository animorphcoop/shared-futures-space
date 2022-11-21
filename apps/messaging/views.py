# pyre-strict

from django.views.generic.base import TemplateView
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import get_template
from userauth.models import CustomUser  # pyre-ignore[21]
from userauth.util import get_system_user  # pyre-ignore[21]
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse
from typing import Dict, List, Any

from .models import Chat, Message, Flag
from river.util import get_chat_containing_river  # pyre-ignore[21]
from river.models import RiverMembership  # pyre-ignore[21]


# usage note: you must redefine post and get_context_data
# both need to be passed three kwargs:
#   a list of users called 'members' which is the people allowed to post in the chat
#   a Chat called 'chat'
#   a str called 'url'
# your get_context_data should define user_anonymous_message and not_member_message in context

class ChatView(TemplateView):
    def post(self, request: WSGIRequest, chat: Chat, members: List[CustomUser], # pyre-ignore[11] - says CustomUser isn't defined as a type?
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
                                                                                 river=get_chat_containing_river(chat)).exists():
                m = Message.objects.get(uuid=request.POST['starter_hide'])
                m.hidden = not m.hidden
                m.save()
            if 'retrieve_messages' in request.POST:
                msg_from, msg_no = 0, 10  # how many messages back to begin, and how many to retrieved
                if ('from' in self.request.POST and self.request.POST['from'].isdigit()):
                    msg_from = int(self.request.POST['from'])
                if ('interval' in self.request.POST and self.request.POST['interval'].isdigit()):
                    msg_no = int(self.request.POST['interval'])
                messages = Message.objects.filter(chat=chat).order_by('timestamp')
                starter_membership = RiverMembership.objects.filter(starter=True, river=get_chat_containing_river(chat))
                context = {'messages': messages[max(0, len(messages) - (msg_no + msg_from)): len(messages) - msg_from], 'chat_view_url' : url,
                           'my_flags' : [flag.message.uuid for flag in Flag.objects.filter(flagged_by=self.request.user)] if self.request.user.is_authenticated else [],
                           'starter' : starter_membership[0].user if len(starter_membership) != 0 else None,
                           'user' : request.user}
                return HttpResponse(get_template('messaging/messages_snippet.html').render(context))
            else :
                return super().post(request)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        msg_from, msg_no = 0, 50  # how many messages back to begin, and how many to retrieve
        if ('from' in self.request.GET and self.request.GET['from'].isdigit()):
            msg_from = int(self.request.GET['from'])
        if ('interval' in self.request.GET and self.request.GET['interval'].isdigit()):
            msg_no = int(self.request.GET['interval'])
        messages = Message.objects.filter(chat=kwargs['chat']).order_by('timestamp')
        #context['user_anonymous_message'] = 'Please log in to participate'
        context['not_member_message'] = 'Join the river to get involved in the conversation!'
        context['messages'] = messages[max(0, len(messages) - (msg_no + msg_from)): len(messages) - msg_from]
        context['more_back'] = msg_no + msg_from < len(messages)
        context['interval'] = msg_no
        context['from'] = msg_from
        context['back_from'] = int(min(msg_from + (msg_no / 2), len(messages)))
        context['forward_from'] = int(max(msg_from - (msg_no / 2), 0))
        context['members'] = kwargs['members']
        context['system_user'] = get_system_user()
        return context
