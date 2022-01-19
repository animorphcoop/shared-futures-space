# pyre-strict

from django.views.generic.base import TemplateView
from django.core.handlers.wsgi import WSGIRequest
from userauth.models import CustomUser # pyre-ignore[21]
from django.shortcuts import redirect
from django.http import HttpResponse
from typing import Dict, List, Any
from django.utils import timezone
from .models import Chat, Message

# usage note: you must redefine post and get_context_data
# both need to be passed three kwargs:
#   a list of users called 'members' which is the people allowed to post in the chat
#   a Chat called 'chat'
#   a str called 'url'
# your get_context_data should define user__anonymous_message and not_member_message in context

class ChatView(TemplateView):
    def post(self, request: WSGIRequest, chat: Chat, members: List[CustomUser], url: str) -> HttpResponse: # pyre-ignore[11] - says CustomUser isn't defined as a type?
        msg_from, msg_no = 0, 50 # how many messages back to begin, and how many to retrieve
        if ('from' in self.request.GET and self.request.GET['from'].isdigit()): # pyre-ignore[16]
            msg_from = int(self.request.GET['from'])
        if ('interval' in self.request.GET and self.request.GET['interval'].isdigit()):
            msg_no = int(self.request.GET['interval'])
        if (request.user in members and 'message' in request.POST):
            new_msg = Message(timestamp=timezone.now(), sender=request.user, text=request.POST['message'], chat=chat) # pyre-ignore[16]
            new_msg.save()
        if ('from' in request.GET and request.GET['from'].isdigit() and int(request.GET['from']) != 0):
            msg_from = 0 # drop to current position in chat if not there already after sending a message
        # redirect so reloading the page doesn't resend the message
        return redirect(url + '?interval=' + str(msg_no) + '&from=' + str(msg_from))
    def get_context_data(self, **kwargs: Dict[str,Any]) -> Dict[str,Any]:
        context = super().get_context_data(**kwargs)
        msg_from, msg_no = 0, 50 # how many messages back to begin, and how many to retrieve
        if ('from' in self.request.GET and self.request.GET['from'].isdigit()): # pyre-ignore[16]
            msg_from = int(self.request.GET['from'])
        if ('interval' in self.request.GET and self.request.GET['interval'].isdigit()):
            msg_no = int(self.request.GET['interval'])
        messages = Message.objects.filter(chat=kwargs['chat']).order_by('timestamp') # pyre-ignore[16]
        context['user_anonymous_message'] = '(you are not logged in)'
        context['not_member_message'] = '(you are not a member of this chat)'
        context['messages'] = messages[max(0,len(messages) - (msg_no + msg_from)) : len(messages) - msg_from]
        context['more_back'] = msg_no + msg_from < len(messages)
        context['interval'] = msg_no
        context['from'] = msg_from
        context['back_from'] = int(min(msg_from + (msg_no/2), len(messages)))
        context['forward_from'] = int(max(msg_from - (msg_no/2), 0))
        context['members'] = kwargs['members']
        context['system_user'] = CustomUser.objects.get(id=0, display_name='SYSTEM USER')
        return context
