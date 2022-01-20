# pyre-strict

import os
from django.template import Template, Context
from messaging.models import Message
from userauth.util import get_system_user, get_userpair
from userauth.models import CustomUser

def send_system_message(user_from, to, kind, context_action = None, context_user_a = None, context_user_b = None):
    Message.objects.create(sender = get_system_user(), text='',
                           snippet = {'offer_of_ownership': 'messaging/system_messages/offer_of_ownership.html',
                                      'new_owner': 'messaging/system_messages/new_owner.html',
                                      }[kind],
                           chat=get_userpair(user_from, to).chat if type(to)==CustomUser else to.chat,
                           context_action = context_action,
                           context_user_a = context_user_a,
                           context_user_b = context_user_b)
