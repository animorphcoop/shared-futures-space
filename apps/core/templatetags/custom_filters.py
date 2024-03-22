import json
from typing import Iterable, List, Optional, TypeVar

from django import template
from map.markers import river_marker
from river.models import River

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


@register.filter(name="lookup")
def lookup(value, arg):
    """Use to get dictionary values out

    if foo is: { "bar": "yay"}

    This will output "yay": {{ foo:lookup:"bar" }}
    """
    return value.get(arg, None)


@register.filter(name="to_marker_json")
def to_marker_json(river: Optional[River]):
    if not river:
        return json.dumps(None)
    return json.dumps(river_marker(river))
