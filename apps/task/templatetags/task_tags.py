from django import template
from django.template import RequestContext
from river.models import RiverMembership
from task.models import Task

register = template.Library()


@register.simple_tag(takes_context=True)
def task_list_id(context: RequestContext) -> str:
    slug = context.get("slug", None)
    stage = context.get("stage", None)
    topic = context.get("topic", None)
    if slug and stage and topic:
        return "-".join(
            [
                "task-list",
                slug,
                stage,
                topic,
            ]
        )
    return ""


@register.simple_tag(takes_context=True)
def task_is_editable(context: RequestContext, task: Task) -> bool:
    """Check if task is editable

    - river starters can edit any task in the river
    - others can only edit what they are responsible for
    """
    user = context.request.user
    slug = context.get("slug", None)
    if task.responsible_id == context.request.user.id:
        return True
    elif (
        slug
        and RiverMembership.objects.filter(
            river__slug=slug,
            user=user,
            starter=True,
        ).exists()
    ):
        return True
    return False
