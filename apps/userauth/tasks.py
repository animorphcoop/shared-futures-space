from collections import defaultdict
from datetime import date
from time import sleep

from analytics.models import has_visited_today
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage, send_mass_mail
from django.utils import timezone
from messaging.models import Message
from river.models import River, RiverMembership
from userauth.models import UserPair


# Send email asynchronously with a delay.
@shared_task
def send_after(duration: float, message: EmailMessage) -> None:
    sleep(duration)
    message.send()


def get_direct_message_data():
    """
    Returns two tuples with info about users' direct messages from current day.
    """
    count_dict = defaultdict(int)
    receivers_dict = defaultdict(set)

    # iterate over all user pairs to find all DM chats
    user_pair_list = UserPair.objects.filter(blocked=False)
    for user_pair in user_pair_list:
        # iterate over all today's messages and see if they belong in the current chat
        today = timezone.now().date()
        message_list = Message.objects.filter(
            timestamp__date=today,
            chat=user_pair.chat,
        )
        for message in message_list:
            # for every message, save receiver
            if message.sender == user_pair.user1:
                receiver = user_pair.user2
            else:
                receiver = user_pair.user1

            # skip receiver if they have logged in today
            if has_visited_today(receiver):
                continue

            count_dict[receiver] += 1
            receivers_dict[receiver].add(message.sender.display_name)

    # return a tuple of two dicts
    return count_dict, receivers_dict


def get_river_chat_set(river):
    """Return all active chats of river, depending on current river stage."""
    chat_set = set()
    if river.current_stage == River.Stage.ENVISION:
        chat_set = {river.envision_stage.general_chat}
    elif river.current_stage == River.Stage.PLAN:
        chat_set = {
            river.plan_stage.general_chat,
            river.plan_stage.money_chat,
            river.plan_stage.place_chat,
            river.plan_stage.time_chat,
        }
    elif river.current_stage == River.Stage.ACT:
        chat_set = {
            river.act_stage.general_chat,
            river.act_stage.money_chat,
            river.act_stage.place_chat,
            river.act_stage.time_chat,
        }
    elif river.current_stage == River.Stage.REFLECT:
        chat_set = {river.reflect_stage.general_chat}

    return chat_set


def get_river_message_data():
    """
    Returns two tuples with info about each users' new messages. One about
    message count and another with the river titles with new messages.
    """
    river_dict = defaultdict(set)
    count_dict = defaultdict(int)

    # for each river
    #   get all river members
    #   for each member of current river
    #     for each message of river's chats
    #       increment `count_dict` (user:count, each user has a number of messages waiting for them)
    #       increment `river_dict` (user:set, each user has a set of river titles that have messages for them)
    #
    # nb. we use a set because there might be many messages in the same river,
    # and we only want to store the river title once
    for river in River.objects.all():
        river_chats = get_river_chat_set(river)
        # for each member of this river,
        # we add the info we need to the dicts that will be returned
        for membership in RiverMembership.objects.filter(river=river):
            # skip user if they have logged in today
            if has_visited_today(membership.user):
                continue

            today = timezone.now().date()
            message_list = Message.objects.filter(
                timestamp__date=today, chat__in=river_chats
            )
            for message in message_list:
                count_dict[membership.user] += 1
                river_dict[membership.user].add(membership.river.title)

    # return a tuple of two dicts
    return count_dict, river_dict


@shared_task
def send_daily_messages() -> None:
    email_list = []
    direct_count_dict, direct_message_dict = get_direct_message_data()
    river_count_dict, river_message_dict = get_river_message_data()

    all_receivers = set(direct_message_dict.keys()) | set(river_message_dict.keys())

    for user in all_receivers:
        message_count = river_count_dict[user] + direct_count_dict[user]
        body = str(message_count)
        body += " new message(s) waiting for you on Shared Futures Space."

        river_set = river_message_dict[user]
        if river_set:
            river_string = "\n".join(river_set)
            body += f"\n\nRivers with messages:\n{river_string}\n"

        senders_set = direct_message_dict[user]
        if senders_set:
            senders_string = "\n".join(senders_set)
            body += f"\n\nUsers who messaged you:\n{senders_string}\n"

        email_list.append(
            (
                "New messages for you on Shared Futures Space",
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        )

    send_mass_mail(email_list)
