import json
from typing import Iterable, List, TypeVar

from django import template
from django.utils.safestring import SafeString, mark_safe
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


@register.filter(name="to_range")
def to_range(number: int):
    return range(number)


@register.filter(name="to_json")
def to_json(value):
    return json.dumps(value)
