# pyre-strict

import os
from django.template import Template, Context
from messaging.models import Message, Chat # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]
from project.models import Project # pyre-ignore[21]
from action.models import Action # pyre-ignore[21]
from poll.models import Poll # pyre-ignore[21]
from uuid import UUID


from typing import Union, Optional

def send_system_message(chat: Chat, kind: str, # pyre-ignore[11]
                        context_action: Optional[Action] = None, context_project: Optional[Project] = None, # pyre-ignore[11]
                        context_user_a: Optional[CustomUser] = None, context_user_b: Optional[CustomUser] = None, # pyre-ignore[11]
                        context_poll: Optional[Poll] = None) -> None: # pyre-ignore[11]
    Message.objects.create(sender = get_system_user(), text='',
                           snippet = {'offer_of_ownership': 'messaging/system_messages/offer_of_ownership.html',
                                      'offer_of_championship': 'messaging/system_messages/offer_of_championship.html',
                                      'new_owner': 'messaging/system_messages/new_owner.html',
                                      'new_champion': 'messaging/system_messages/new_champion.html',
                                      'lost_ownership': 'messaging/system_messages/lost_ownership.html',
                                      'lost_championship': 'messaging/system_messages/lost_championship.html',
                                      'lost_championship_notification': 'messaging/system_messages/lost_championship_notification.html',
                                      'left_project': 'messaging/system_messages/left_project.html',
                                      'joined_project': 'messaging/system_messages/joined_project.html',
                                      'user_request': 'messaging/system_messages/user_request.html',
                                      'request_accepted': 'messaging/system_messages/request_accepted.html',
                                      'request_rejected': 'messaging/system_messages/request_rejected.html',
                                      'poll': 'messaging/poll/view_poll.html'
                                      }[kind],
                           chat=chat,
                           context_action = context_action,
                           context_project = context_project,
                           context_user_a = context_user_a,
                           context_user_b = context_user_b,
                           context_poll = context_poll)

def get_requests_chat() -> Chat:
    return Chat.objects.get_or_create(uuid=UUID('00000000-0000-0000-0000-000000000000'))[0]
