# pyre-strict

import os
from django.template import Template, Context
from messaging.models import Message # pyre-ignore[21]
from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]
from project.models import Project # pyre-ignore[21]
from action.models import Action # pyre-ignore[21]

from typing import Union, Optional

def send_system_message(user_from: CustomUser, to: Union[CustomUser,Project], kind: str, # pyre-ignore[11]
                        context_action: Optional[Action] = None, context_user_a: Optional[CustomUser] = None, # pyre-ignore[11]
                        context_user_b: Optional[CustomUser] = None) -> None:
    Message.objects.create(sender = get_system_user(), text='',
                           snippet = {'offer_of_ownership': 'messaging/system_messages/offer_of_ownership.html',
                                      'new_owner': 'messaging/system_messages/new_owner.html',
                                      }[kind],
                           chat=get_userpair(user_from, to).chat if type(to)==CustomUser else to.chat,
                           context_action = context_action,
                           context_user_a = context_user_a,
                           context_user_b = context_user_b)
