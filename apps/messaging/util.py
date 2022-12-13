# pyre-strict

import os
from django.template import Template, Context
from messaging.models import Message, Chat # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]
from poll.models import BasePoll # pyre-ignore[21]
from uuid import UUID


from typing import Union, Optional

def send_system_message(chat: Chat, kind: str,  # pyre-ignore[11]
                        context_action: Optional['action.Action'] = None, context_river: Optional['river.River'] = None,  # pyre-ignore[11]
                        context_user_a: Optional[CustomUser] = None, context_user_b: Optional[CustomUser] = None,  # pyre-ignore[11]
                        context_poll: Optional[BasePoll] = None) -> None: # pyre-ignore[11]
    Message.objects.create(sender = get_system_user(), text='',
                           snippet = {'offer_of_ownership': 'messaging/system_messages/offer_of_ownership.html',
                                      'removed_from_river': 'messaging/system_messages/removed_from_river.html',
                                      'new_owner': 'messaging/system_messages/new_owner.html',
                                      'left_project': 'messaging/system_messages/left_project.html',
                                      'joined_project': 'messaging/system_messages/joined_project.html',
                                      'user_request': 'messaging/system_messages/user_request.html',
                                      'request_accepted': 'messaging/system_messages/request_accepted.html',
                                      'request_rejected': 'messaging/system_messages/request_rejected.html',
                                      'poll': 'messaging/system_messages/poll.html',
                                      'finished_envision': 'messaging/system_messages/finished_envision.html',
                                      'blocked user': 'messaging/system_messages/user_chat_blocked.html',
                                      }[kind],
                           chat=chat,
                           context_action = context_action,
                           context_river = context_river,
                           context_user_a = context_user_a,
                           context_user_b = context_user_b,
                           context_poll = context_poll)

def get_requests_chat() -> Chat:
    return Chat.objects.get_or_create(uuid=UUID('00000000-0000-0000-0000-000000000000'))[0]
