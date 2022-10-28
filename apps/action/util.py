# pye-strict

from userauth.util import get_system_user, get_userpair # pyre-ignore[21]
from messaging.util import send_system_message, get_userpair # pyre-ignore[21]
from django.utils.html import escape
from messaging.models import Message # pyre-ignore[21]
from django.urls import reverse
from .models import Action

def send_offer(user_from, user_to, kind, param_river = None):
    existing_offers = Action.objects.filter(receiver=user_to, kind=kind, param_river=param_river, result__isnull = True)
    for offer in existing_offers: # remove any duplicates automatically
        offer.result = 'rescinded'
        offer.save()
    action = Action.objects.create(creator=user_from, receiver=user_to, kind=kind, param_project=param_project)   
    if kind == 'become_starter':
        send_system_message(get_userpair(user_from, user_to).chat, 'offer_of_ownership', context_action = action)
