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
from userauth.models import CustomUser


# Send email asynchronously with a delay.
@shared_task
def send_after(duration: float, message: EmailMessage) -> None:
    sleep(duration)
    message.send()


def get_direct_message_data():
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
            count_dict[receiver] += 1
            receivers_dict[receiver].add(message.sender.display_name)

    # return a tuple of two dicts
    return count_dict, receivers_dict


def get_river_message_data():
    """
    Returns two tuples with info about each users new messages. One about
    message count and another with the river titles with new messages.
    """
    river_dict = defaultdict(set)
    count_dict = defaultdict(int)

    # for each river
    #   get all river members
    #   for each member of current river
    #     for each message of river's chats
    #       increment `river_dict` (user:count, each user has a number of messages waiting for them)
    #       increment `river_dict` (user:set, each user has a set of river titles that have messages for them)
    #
    # nb. we use a set because there might be many messages in the same river,
    # and we only want to store the river title once
    for river in River.objects.all():
        # find chat list
        chat_list = []
        if river.current_stage == River.Stage.ENVISION:
            chat_list = [river.envision_stage.general_chat]
        elif river.current_stage == River.Stage.PLAN:
            chat_list = [
                river.plan_stage.general_chat,
                river.plan_stage.money_chat,
                river.plan_stage.place_chat,
                river.plan_stage.time_chat,
            ]
        elif river.current_stage == River.Stage.ACT:
            chat_list = [
                river.act_stage.general_chat,
                river.act_stage.money_chat,
                river.act_stage.place_chat,
                river.act_stage.time_chat,
            ]
        elif river.current_stage == River.Stage.REFLECT:
            chat_list = [river.reflect_stage.general_chat]

        # for each member of this river,
        # we add the info we need to the dicts that will be returned
        for membership in RiverMembership.objects.filter(river=river):

            # skip user if they have logged in today
            if has_visited_today(membership.user):
                continue

            today = timezone.now().date()
            message_list = Message.objects.filter(
                timestamp__date=today, chat__in=chat_list
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

    for user in river_count_dict:
        message_count = river_count_dict[user]

        # add direct messages in total count
        if user in direct_count_dict:
            message_count += direct_count_dict[user]

        river_set = river_message_dict[user]
        river_string = "\n".join(river_set)
        body = f"""
{message_count} new message(s) waiting for you on Shared Futures Space.

Rivers with messages:
{river_string}
        """

        # add direct messages that user received, if they exist
        if user in direct_message_dict:
            senders_set = direct_message_dict[user]
            senders_string = "\n".join(senders_set)
            body += f"\n\nUsers who messaged you:\n{senders_string}\n"

        email_list.append(
            EmailMessage(
                subject=f"New messages for you on Shared Futures Space",
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
        )

    send_mass_mail(email_list)
