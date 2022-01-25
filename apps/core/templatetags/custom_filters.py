# pyre-strict
from django import template
from django.http import HttpResponse
from typing import Iterable, List, Any, TypeVar, Dict

register = template.Library()

T = TypeVar('T')
@register.filter(name='attrmap')
def attrmap(value: Iterable[T], arg: str) -> List[T]:
    if hasattr(value, '__iter__'):
        return [getattr(item, arg) for item in value]
    else:
        return []

@register.simple_tag(takes_context = True, name = 'include_text')
def include_text(context: Dict[str,Any], text: str) -> HttpResponse:
    return template.Template(text).render(context=context)
