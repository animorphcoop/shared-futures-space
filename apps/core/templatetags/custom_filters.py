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
