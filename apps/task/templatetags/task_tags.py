from django import template
from django.conf import settings
from django.template import RequestContext
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def task_list_id(context: RequestContext):
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
    return None
