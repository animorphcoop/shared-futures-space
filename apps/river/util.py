# pyre-strict
from django.utils import timezone

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

'''
def get_current_stage_string(current_stage) -> str:
    stage_switch= {
      "envision":'Stage 1: Envision',
      "plan":'Stage 1: Plan',
      "act":'Stage 1: Act',
      "reflect":'Stage 1: Reflect'
      }
    return stage_switch.get(current_stage, "")


def get_started_months_ago(started_on):
    print(timezone.now()-started_on)
    return timezone.now().month - started_on.month
'''