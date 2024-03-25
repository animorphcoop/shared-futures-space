from typing import Optional

from django.db.models import Q
from messaging.models import Chat
from resources.models import Resource

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


def get_resource_tags() -> list[str]:
    tags = []
    resources = Resource.objects.all()

    for resource in resources:
        for tag in resource.tags.names():
            if tag.lower() not in tags:
                tags.append(tag.lower())

    tags.sort()
    return tags
