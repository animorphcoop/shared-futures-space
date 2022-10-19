# pyre-strict
from django import template
from ..models import Area

from typing import List

register = template.Library()

# get areas, exclude 'other' from the list and sort alphabetically
@register.simple_tag
def get_areas() -> List[str]:
    areas = []
    for area in Area.objects.all():
        if area.name != 'Other':
            areas.append(area.name)
    areas.sort()
    print(type(areas))
    return areas

