# pyre-strict
from django import template
from ..models import Area

register = template.Library()

# get areas, exclude 'other' from the list and sort alphabetically
@register.simple_tag
def get_areas():
    areas = []
    for area in Area.objects.all():
        if area.name != 'Other':
            areas.append(area.name)
    areas.sort()
    return areas

