import random
from typing import Optional

from django.db.models import Q
from django.template.loader import render_to_string

from messaging.models import Chat

from .models import ActStage, EnvisionStage, PlanStage, ReflectStage, River


def get_chat_containing_river(chat: Chat) -> Optional[River]:
    # return the river that a chat is part of, if any
    envision = EnvisionStage.objects.filter(chat=chat)
    if len(envision) != 0:
        return River.objects.get(envision_stage=envision[0])
    plan = PlanStage.objects.filter(
        Q(general_chat=chat)
        | Q(money_chat=chat)
        | Q(place_chat=chat)
        | Q(time_chat=chat)
    )
    if len(plan) != 0:
        return River.objects.get(plan_stage=plan[0])
    act = ActStage.objects.filter(
        Q(general_chat=chat)
        | Q(money_chat=chat)
        | Q(place_chat=chat)
        | Q(time_chat=chat)
    )
    if len(act) != 0:
        return River.objects.get(act_stage=act[0])
    reflect = ReflectStage.objects.filter(chat=chat)
    if len(reflect) != 0:
        return River.objects.get(reflect_stage=reflect[0])
    return None


def river_marker(river: River) -> Optional[dict]:
    if not river.location:
        return None
    return {
        "slug": river.slug,
        "name": river.title,
        "icon": "pin",
        "coordinates": river.location.coords,
        "html": render_to_string(
            "river/river_card.html",
            {"river": river, "close_button": True, "view_button": True},
        ),
        "htmlMini": render_to_string("river/river_card_mini.html", {"river": river}),
    }
