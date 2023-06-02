import os
from django.template import Template, Context
from messaging.models import Message, Chat
from userauth.util import get_system_user, get_userpair
from userauth.models import CustomUser
from poll.models import BasePoll
from uuid import UUID

from typing import Union, Optional


def send_system_message(chat: Chat, kind: str,
                        context_action: Optional['action.Action'] = None, context_river: Optional['river.River'] = None,
                        context_user_a: Optional[CustomUser] = None, context_user_b: Optional[CustomUser] = None,
                        context_poll: Optional[BasePoll] = None,
                        text: Optional[str] = "",
                        ) -> None:
    Message.objects.create(sender=get_system_user(), text=text,
                           snippet={'offer_of_ownership': 'messaging/system_messages/offer_of_ownership.html',
                                    'ownership_determined': 'messaging/system_messages/ownership_determined.html',
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
                                    'salmon_envision_start': 'messaging/system_messages/salmon_envision_start.html',
                                    'salmon_envision_intro': 'messaging/system_messages/salmon_envision_intro.html',
                                    'salmon_envision_swimmers': 'messaging/system_messages/salmon_envision_swimmers.html',
                                    'salmon_envision_poll': 'messaging/system_messages/salmon_envision_poll.html',
                                    'salmon_envision_poll_available': 'messaging/system_messages/salmon_envision_poll_available.html',
                                    'salmon_wizard': 'messaging/system_messages/salmon_wizard.html',
                                    'poll_edited': 'messaging/system_messages/poll_edited.html',

                                    }[kind],
                           chat=chat,
                           context_action=context_action,
                           context_river=context_river,
                           context_user_a=context_user_a,
                           context_user_b=context_user_b,
                           context_poll=context_poll)


def get_requests_chat() -> Chat:
    return Chat.objects.get_or_create(uuid=UUID('00000000-0000-0000-0000-000000000000'))[0]
