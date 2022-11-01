# pyre-strict

from django.db.models import Q

from .models import River, EnvisionStage, PlanStage, ActStage, ReflectStage
from messaging.models import Chat # pyre-ignore[21]

from typing import Optional

def get_chat_containing_river(chat: Chat) -> Optional[River]: # pyre-ignore[11]
    # return the river that a chat is part of, if any
    envision = EnvisionStage.objects.filter(chat  = chat)
    if len(envision) != 0:
        return River.objects.get(envision_stage = envision[0])
    plan = PlanStage.objects.filter(Q(general_chat = chat) | Q(funding_chat = chat) | Q(location_chat = chat) | Q(dates_chat = chat))
    if len(plan) != 0:
        return River.objects.get(plan_stage = plan[0])
    act = ActStage.objects.filter(Q(general_chat = chat) | Q(funding_chat = chat) | Q(location_chat = chat) | Q(dates_chat = chat))
    if len(act) != 0:
        return River.objects.get(act_stage = act[0])
    reflect = ReflectStage.objects.filter(chat  = chat)
    if len(reflect) != 0:
        return River.objects.get(reflect_stage = reflect[0])
    return None
