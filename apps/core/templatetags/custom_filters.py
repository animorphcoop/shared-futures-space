from typing import Iterable, List, TypeVar

from django import template
from django.utils.timesince import timesince, timeuntil

register = template.Library()

T = TypeVar("T")


@register.filter(name="attrmap")
def attrmap(value: Iterable[T], arg: str) -> List[T]:
    if hasattr(value, "__iter__"):
        return [getattr(item, arg) for item in value]
    else:
        return []


@register.filter(name="strcat")
def strcat(value, arg):
    return str(value) + str(arg)
